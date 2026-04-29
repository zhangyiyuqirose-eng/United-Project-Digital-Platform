package com.bank.updg.updg_project.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.bank.updg.common.exception.BusinessException;
import com.bank.updg.common.model.enums.ErrorCodeEnum;
import com.bank.updg.updg_project.mapper.ProjectMapper;
import com.bank.updg.updg_project.mapper.ProjectRiskMapper;
import com.bank.updg.updg_project.mapper.ProjectTaskMapper;
import com.bank.updg.updg_project.model.entity.Project;
import com.bank.updg.updg_project.model.entity.ProjectRisk;
import com.bank.updg.updg_project.model.entity.ProjectTask;
import com.bank.updg.updg_project.service.HealthScoreService;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.math.BigDecimal;
import java.math.RoundingMode;
import java.time.LocalDate;
import java.time.LocalDateTime;
import java.util.List;

@Service
@RequiredArgsConstructor
public class HealthScoreServiceImpl implements HealthScoreService {

    private static final BigDecimal WEIGHT_SCHEDULE = new BigDecimal("0.30");
    private static final BigDecimal WEIGHT_COST = new BigDecimal("0.30");
    private static final BigDecimal WEIGHT_RISK = new BigDecimal("0.20");
    private static final BigDecimal WEIGHT_TASK = new BigDecimal("0.20");
    private static final BigDecimal HUNDRED = new BigDecimal("100");

    private final ProjectMapper projectMapper;
    private final ProjectTaskMapper taskMapper;
    private final ProjectRiskMapper riskMapper;

    @Override
    public BigDecimal computeHealthScore(String projectId) {
        Project project = projectMapper.selectById(projectId);
        if (project == null) {
            throw new BusinessException(ErrorCodeEnum.PARAM_ERROR, "Project not found: " + projectId);
        }

        // 1. Schedule variance score (30%)
        BigDecimal scheduleScore = computeScheduleScore(project);

        // 2. Cost variance score - CPI based (30%)
        BigDecimal costScore = computeCostScore(project);

        // 3. Risk level score (20%)
        BigDecimal riskScore = computeRiskScore(projectId);

        // 4. Task completion score (20%)
        BigDecimal taskScore = computeTaskCompletionScore(projectId);

        // Weighted sum
        BigDecimal healthScore = scheduleScore.multiply(WEIGHT_SCHEDULE)
                .add(costScore.multiply(WEIGHT_COST))
                .add(riskScore.multiply(WEIGHT_RISK))
                .add(taskScore.multiply(WEIGHT_TASK))
                .setScale(2, RoundingMode.HALF_UP);

        // Clamp to 0-100
        if (healthScore.compareTo(BigDecimal.ZERO) < 0) {
            healthScore = BigDecimal.ZERO;
        }
        if (healthScore.compareTo(HUNDRED) > 0) {
            healthScore = HUNDRED;
        }

        return healthScore;
    }

    /**
     * Schedule score: based on actual vs planned progress.
     * Uses SPI if available, otherwise computes from dates.
     */
    private BigDecimal computeScheduleScore(Project project) {
        if (project.getEvmSpi() != null && project.getEvmSpi().compareTo(BigDecimal.ZERO) > 0) {
            // SPI >= 1.0 -> 100, SPI < 1.0 -> SPI * 100
            BigDecimal spi = project.getEvmSpi();
            if (spi.compareTo(BigDecimal.ONE) >= 0) {
                return HUNDRED;
            }
            return spi.multiply(HUNDRED).min(HUNDRED).max(BigDecimal.ZERO);
        }

        // Fallback: compute from start/end dates and current date
        if (project.getStartTime() != null && project.getEndTime() != null) {
            LocalDateTime now = LocalDateTime.now();
            long totalDays = java.time.Duration.between(project.getStartTime(), project.getEndTime()).toDays();
            long elapsedDays = java.time.Duration.between(project.getStartTime(), now).toDays();

            if (totalDays <= 0) return HUNDRED;

            BigDecimal expectedProgress = BigDecimal.valueOf(elapsedDays)
                    .multiply(HUNDRED)
                    .divide(BigDecimal.valueOf(totalDays), 2, RoundingMode.HALF_UP)
                    .min(HUNDRED);

            // Actual progress from WBS or default 0
            BigDecimal actualProgress = BigDecimal.ZERO;
            if (project.getWbsJson() != null && !project.getWbsJson().isEmpty()) {
                // Estimate actual progress - if SPI available use it, else assume 50% if in progress
                if (project.getStatus() != null && !project.getStatus().equals("DRAFT")) {
                    actualProgress = new BigDecimal("50");
                }
            }

            if (expectedProgress.compareTo(BigDecimal.ZERO) == 0) return HUNDRED;
            return actualProgress.multiply(HUNDRED)
                    .divide(expectedProgress, 2, RoundingMode.HALF_UP)
                    .min(HUNDRED)
                    .max(BigDecimal.ZERO);
        }

        return HUNDRED; // No schedule data, assume on track
    }

    /**
     * Cost score: based on CPI from EVM.
     * CPI >= 1.0 -> 100, CPI < 1.0 -> CPI * 100
     */
    private BigDecimal computeCostScore(Project project) {
        if (project.getEvmCpi() != null && project.getEvmCpi().compareTo(BigDecimal.ZERO) > 0) {
            BigDecimal cpi = project.getEvmCpi();
            if (cpi.compareTo(BigDecimal.ONE) >= 0) {
                return HUNDRED;
            }
            return cpi.multiply(HUNDRED).min(HUNDRED).max(BigDecimal.ZERO);
        }
        return HUNDRED; // No cost data, assume on budget
    }

    /**
     * Risk score: penalized by count of high/critical risks.
     * Each critical risk deducts 25 points, each high deducts 15 points.
     */
    private BigDecimal computeRiskScore(String projectId) {
        LambdaQueryWrapper<ProjectRisk> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(ProjectRisk::getProjectId, projectId)
                .in(ProjectRisk::getStatus, "IDENTIFIED", "ASSESSED", "MITIGATING", "MATERIALIZED");
        List<ProjectRisk> activeRisks = riskMapper.selectList(wrapper);

        BigDecimal deduction = BigDecimal.ZERO;
        for (ProjectRisk risk : activeRisks) {
            if ("CRITICAL".equals(risk.getSeverity())) {
                deduction = deduction.add(new BigDecimal("25"));
            } else if ("HIGH".equals(risk.getSeverity())) {
                deduction = deduction.add(new BigDecimal("15"));
            } else if ("MEDIUM".equals(risk.getSeverity())) {
                deduction = deduction.add(new BigDecimal("5"));
            }
        }

        BigDecimal score = HUNDRED.subtract(deduction);
        return score.max(BigDecimal.ZERO);
    }

    /**
     * Task completion score: completed tasks / total tasks * 100.
     */
    private BigDecimal computeTaskCompletionScore(String projectId) {
        LambdaQueryWrapper<ProjectTask> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(ProjectTask::getProjectId, projectId);
        List<ProjectTask> tasks = taskMapper.selectList(wrapper);

        if (tasks.isEmpty()) {
            return HUNDRED; // No tasks, assume on track
        }

        long completed = tasks.stream()
                .filter(t -> "DONE".equals(t.getStatus()))
                .count();

        return BigDecimal.valueOf(completed)
                .multiply(HUNDRED)
                .divide(BigDecimal.valueOf(tasks.size()), 2, RoundingMode.HALF_UP);
    }
}
