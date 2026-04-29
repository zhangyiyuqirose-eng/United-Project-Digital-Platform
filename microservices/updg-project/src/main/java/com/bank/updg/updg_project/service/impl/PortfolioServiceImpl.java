package com.bank.updg.updg_project.service.impl;

import com.bank.updg.updg_project.model.entity.Project;
import com.bank.updg.updg_project.model.entity.ProjectRisk;
import com.bank.updg.updg_project.service.PortfolioService;
import com.bank.updg.updg_project.service.ProjectService;
import com.bank.updg.updg_project.service.RiskService;
import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.math.BigDecimal;
import java.util.*;
import java.util.stream.Collectors;

/**
 * Portfolio dashboard implementation.
 * Aggregates project-level data into portfolio-wide metrics.
 */
@Service
@RequiredArgsConstructor
public class PortfolioServiceImpl implements PortfolioService {

    private final ProjectService projectService;
    private final RiskService riskService;

    @Override
    public Map<String, Object> getSummary() {
        List<Project> allProjects = projectService.list();

        // Projects by status
        Map<String, Long> projectsByStatus = allProjects.stream()
                .collect(Collectors.groupingBy(
                        p -> p.getStatus() != null ? p.getStatus() : "UNKNOWN",
                        Collectors.counting()));

        // Total budget vs actual
        BigDecimal totalBudget = allProjects.stream()
                .map(Project::getBudget)
                .filter(Objects::nonNull)
                .reduce(BigDecimal.ZERO, BigDecimal::add);
        BigDecimal totalActual = allProjects.stream()
                .map(Project::getEvmAc)
                .filter(Objects::nonNull)
                .reduce(BigDecimal.ZERO, BigDecimal::add);

        // Risk summary by severity
        List<ProjectRisk> allRisks = riskService.list();
        Map<String, Long> risksBySeverity = allRisks.stream()
                .collect(Collectors.groupingBy(
                        r -> r.getSeverity() != null ? r.getSeverity() : "UNKNOWN",
                        Collectors.counting()));

        // Resource utilization rate
        long activeProjects = allProjects.stream()
                .filter(p -> "ACTIVE".equals(p.getStatus()) || "IN_PROGRESS".equals(p.getStatus()))
                .count();
        double utilizationRate = allProjects.isEmpty() ? 0.0 :
                (double) activeProjects / allProjects.size() * 100;

        return Map.of(
                "projectsByStatus", projectsByStatus,
                "totalBudget", totalBudget,
                "totalActual", totalActual,
                "risksBySeverity", risksBySeverity,
                "resourceUtilizationRate", Math.round(utilizationRate * 100.0) / 100.0
        );
    }

    @Override
    public List<Map<String, Object>> getResourceConflicts() {
        // TODO: Implement proper cross-project resource conflict detection
        // This requires resource assignment data from updg-resource service
        // For now, returns an empty list as placeholder
        return new ArrayList<>();
    }
}
