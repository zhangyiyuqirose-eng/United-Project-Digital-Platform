package com.bank.updg.updg_project.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.bank.updg.common.exception.BusinessException;
import com.bank.updg.common.model.enums.ErrorCodeEnum;
import com.bank.updg.updg_project.mapper.ProjectRiskMapper;
import com.bank.updg.updg_project.model.entity.ProjectRisk;
import com.bank.updg.updg_project.service.RiskService;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.math.BigDecimal;
import java.math.RoundingMode;
import java.time.LocalDateTime;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.UUID;

@Service
@RequiredArgsConstructor
public class RiskServiceImpl implements RiskService {

    private final ProjectRiskMapper riskMapper;

    @Override
    public ProjectRisk createRisk(ProjectRisk risk) {
        risk.setRiskId(UUID.randomUUID().toString().replace("-", ""));
        risk.setRiskCode("RSK-" + System.currentTimeMillis() % 10000);
        risk.setStatus("IDENTIFIED");
        risk.setIdentifiedDate(LocalDateTime.now());
        risk.setCreateTime(LocalDateTime.now());
        risk.setUpdateTime(LocalDateTime.now());
        if (risk.getProbability() != null && risk.getImpact() != null) {
            risk.setRiskScore(risk.getProbability().multiply(BigDecimal.valueOf(risk.getImpact())));
        }
        riskMapper.insert(risk);
        return risk;
    }

    @Override
    public void updateRisk(String riskId, ProjectRisk risk) {
        risk.setRiskId(riskId);
        risk.setUpdateTime(LocalDateTime.now());
        if (risk.getProbability() != null && risk.getImpact() != null) {
            risk.setRiskScore(risk.getProbability().multiply(BigDecimal.valueOf(risk.getImpact())));
        }
        riskMapper.updateById(risk);
    }

    @Override
    public ProjectRisk getRisk(String riskId) {
        ProjectRisk risk = riskMapper.selectById(riskId);
        if (risk == null) {
            throw new BusinessException(ErrorCodeEnum.NOT_FOUND, "Risk not found: " + riskId);
        }
        return risk;
    }

    @Override
    public Page<ProjectRisk> listByProject(String projectId, String status, int page, int size) {
        Page<ProjectRisk> pageObj = new Page<>(page, size);
        LambdaQueryWrapper<ProjectRisk> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(ProjectRisk::getProjectId, projectId);
        if (status != null && !status.isEmpty()) {
            wrapper.eq(ProjectRisk::getStatus, status);
        }
        wrapper.orderByDesc(ProjectRisk::getRiskScore);
        return riskMapper.selectPage(pageObj, wrapper);
    }

    @Override
    public List<ProjectRisk> listHighSeverityRisks() {
        LambdaQueryWrapper<ProjectRisk> wrapper = new LambdaQueryWrapper<>();
        wrapper.in(ProjectRisk::getSeverity, "CRITICAL", "HIGH")
               .notIn(ProjectRisk::getStatus, "CLOSED")
               .orderByDesc(ProjectRisk::getRiskScore);
        return riskMapper.selectList(wrapper);
    }

    @Override
    public void changeStatus(String riskId, String newStatus, String userId) {
        ProjectRisk risk = getRisk(riskId);
        risk.setStatus(newStatus);
        if ("CLOSED".equals(newStatus)) {
            risk.setClosedDate(LocalDateTime.now());
        }
        risk.setUpdateTime(LocalDateTime.now());
        riskMapper.updateById(risk);
    }

    @Override
    public Map<String, Object> getRiskStats(String projectId) {
        LambdaQueryWrapper<ProjectRisk> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(ProjectRisk::getProjectId, projectId);
        List<ProjectRisk> risks = riskMapper.selectList(wrapper);

        Map<String, Object> stats = new HashMap<>();
        stats.put("total", risks.size());
        stats.put("critical", risks.stream().filter(r -> "CRITICAL".equals(r.getSeverity())).count());
        stats.put("high", risks.stream().filter(r -> "HIGH".equals(r.getSeverity())).count());
        stats.put("open", risks.stream().filter(r -> "OPEN".equals(r.getStatus()) || "IDENTIFIED".equals(r.getStatus()) || "ASSESSED".equals(r.getStatus())).count());
        stats.put("closed", risks.stream().filter(r -> "CLOSED".equals(r.getStatus())).count());
        return stats;
    }

    @Override
    public BigDecimal assessRisk(String riskId) {
        ProjectRisk risk = getRisk(riskId);
        if (risk.getProbability() == null || risk.getImpact() == null) {
            throw new BusinessException(ErrorCodeEnum.PARAM_ERROR, "probability and impact are required");
        }
        BigDecimal score = risk.getProbability().multiply(BigDecimal.valueOf(risk.getImpact())).setScale(2, RoundingMode.HALF_UP);
        risk.setRiskScore(score);
        riskMapper.updateById(risk);
        return score;
    }

    @Override
    public List<ProjectRisk> list() {
        return riskMapper.selectList(null);
    }
}
