package com.bank.updg.updg_project.service;

import com.baomidou.mybatisplus.extension.service.IService;
import com.bank.updg.updg_project.model.entity.Project;

import java.math.BigDecimal;
import java.util.Map;

public interface ProjectService extends IService<Project> {

    void initProject(Project project);

    void updateProgress(String projectId, String wbsJson);

    void submitChange(String projectId, String changeType, String content, String reason);

    void closeProject(String projectId, String summary, String costSummary, String lessonsLearned);

    Map<String, Object> getPortfolio();

    void calculateEVM(String projectId, BigDecimal pv, BigDecimal ev, BigDecimal ac);

    /**
     * F-104: Generate a rule-based WBS tree for a project.
     * Returns a standard WBS structure with phases:
     * Initiation, Planning, Execution, Testing, Delivery.
     */
    Map<String, Object> generateWbs(String projectId);
}
