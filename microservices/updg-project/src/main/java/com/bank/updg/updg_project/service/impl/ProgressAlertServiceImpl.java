package com.bank.updg.updg_project.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.bank.updg.updg_project.mapper.ProgressAlertMapper;
import com.bank.updg.updg_project.mapper.ProjectMapper;
import com.bank.updg.updg_project.mapper.ProjectTaskMapper;
import com.bank.updg.updg_project.model.entity.ProgressAlert;
import com.bank.updg.updg_project.model.entity.Project;
import com.bank.updg.updg_project.model.entity.ProjectTask;
import com.bank.updg.updg_project.service.ProgressAlertService;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.math.BigDecimal;
import java.math.RoundingMode;
import java.time.Duration;
import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.List;
import java.util.UUID;

@Service
@RequiredArgsConstructor
public class ProgressAlertServiceImpl implements ProgressAlertService {

    private static final BigDecimal DEVIATION_THRESHOLD = new BigDecimal("15");
    private static final BigDecimal HUNDRED = new BigDecimal("100");

    private final ProgressAlertMapper progressAlertMapper;
    private final ProjectMapper projectMapper;
    private final ProjectTaskMapper taskMapper;

    @Override
    public List<ProgressAlert> checkAllProjects() {
        // Get all active projects
        LambdaQueryWrapper<Project> wrapper = new LambdaQueryWrapper<>();
        wrapper.in(Project::getStatus, "IN_PROGRESS", "PLANNING");
        List<Project> projects = projectMapper.selectList(wrapper);

        List<ProgressAlert> alerts = new ArrayList<>();
        for (Project project : projects) {
            ProgressAlert alert = checkProject(project.getProjectId());
            if (alert != null) {
                alerts.add(alert);
            }
        }
        return alerts;
    }

    @Override
    public ProgressAlert checkProject(String projectId) {
        Project project = projectMapper.selectById(projectId);
        if (project == null) {
            return null;
        }

        // Skip if no timeline
        if (project.getStartTime() == null || project.getEndTime() == null) {
            return null;
        }

        // Compute expected progress based on elapsed time
        LocalDateTime now = LocalDateTime.now();
        long totalDuration = Duration.between(project.getStartTime(), project.getEndTime()).toDays();
        long elapsedDuration = Duration.between(project.getStartTime(), now).toDays();

        if (totalDuration <= 0) return null;

        BigDecimal expectedProgress = BigDecimal.valueOf(elapsedDuration)
                .multiply(HUNDRED)
                .divide(BigDecimal.valueOf(totalDuration), 2, RoundingMode.HALF_UP)
                .min(HUNDRED)
                .max(BigDecimal.ZERO);

        // Compute actual progress from tasks
        List<ProjectTask> tasks = taskMapper.selectList(
                new LambdaQueryWrapper<ProjectTask>().eq(ProjectTask::getProjectId, projectId));

        BigDecimal actualProgress;
        if (tasks.isEmpty()) {
            actualProgress = BigDecimal.ZERO;
        } else {
            int totalProgress = tasks.stream().mapToInt(t -> t.getProgress() != null ? t.getProgress() : 0).sum();
            actualProgress = BigDecimal.valueOf(totalProgress)
                    .divide(BigDecimal.valueOf(tasks.size()), 2, RoundingMode.HALF_UP);
        }

        // Check deviation
        BigDecimal deviation = expectedProgress.subtract(actualProgress).abs();
        if (deviation.compareTo(DEVIATION_THRESHOLD) <= 0) {
            return null;
        }

        // Create alert
        String severity = deviation.compareTo(new BigDecimal("30")) > 0 ? "CRITICAL" : "WARNING";
        ProgressAlert alert = ProgressAlert.builder()
                .alertId(UUID.randomUUID().toString().replace("-", ""))
                .projectId(projectId)
                .alertType("PROGRESS_DEVIATION")
                .message(String.format("Project %s progress deviation: expected %.1f%%, actual %.1f%%, deviation %.1f%%",
                        project.getProjectName(), expectedProgress, actualProgress, deviation))
                .actualProgress(actualProgress)
                .expectedProgress(expectedProgress)
                .deviation(deviation)
                .severity(severity)
                .status("ACTIVE")
                .build();

        progressAlertMapper.insert(alert);
        return alert;
    }

    @Override
    public List<ProgressAlert> getActiveAlerts() {
        LambdaQueryWrapper<ProgressAlert> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(ProgressAlert::getStatus, "ACTIVE")
                .orderByDesc(ProgressAlert::getCreateTime);
        return progressAlertMapper.selectList(wrapper);
    }

    @Override
    public Page<ProgressAlert> listByProject(String projectId, int page, int size) {
        Page<ProgressAlert> pageObj = new Page<>(page, size);
        LambdaQueryWrapper<ProgressAlert> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(ProgressAlert::getProjectId, projectId)
                .orderByDesc(ProgressAlert::getCreateTime);
        return progressAlertMapper.selectPage(pageObj, wrapper);
    }

    @Override
    public void resolveAlert(String alertId) {
        ProgressAlert alert = progressAlertMapper.selectById(alertId);
        if (alert != null) {
            alert.setStatus("RESOLVED");
            alert.setResolveTime(LocalDateTime.now());
            progressAlertMapper.updateById(alert);
        }
    }
}
