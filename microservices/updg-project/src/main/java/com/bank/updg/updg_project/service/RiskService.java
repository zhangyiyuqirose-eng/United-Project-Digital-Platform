package com.bank.updg.updg_project.service;

import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.bank.updg.updg_project.model.entity.ProjectRisk;

import java.math.BigDecimal;
import java.util.List;
import java.util.Map;

public interface RiskService {

    /** Register a new risk for a project. */
    ProjectRisk createRisk(ProjectRisk risk);

    /** Update risk details. */
    void updateRisk(String riskId, ProjectRisk risk);

    /** Get risk by ID. */
    ProjectRisk getRisk(String riskId);

    /** List risks by project with optional status filter. */
    Page<ProjectRisk> listByProject(String projectId, String status, int page, int size);

    /** List high-severity risks across all projects. */
    List<ProjectRisk> listHighSeverityRisks();

    /** Change risk status (with validation). */
    void changeStatus(String riskId, String newStatus, String userId);

    /** Get risk statistics for a project. */
    Map<String, Object> getRiskStats(String projectId);

    /** Assess risk: auto-calculate riskScore = probability * impact. */
    BigDecimal assessRisk(String riskId);

    /** List all risks. */
    List<ProjectRisk> list();
}
