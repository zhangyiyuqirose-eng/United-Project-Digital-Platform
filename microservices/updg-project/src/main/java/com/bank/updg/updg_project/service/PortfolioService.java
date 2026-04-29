package com.bank.updg.updg_project.service;

import java.util.List;
import java.util.Map;

/**
 * Portfolio-level analytics and cross-project resource management.
 */
public interface PortfolioService {

    /**
     * Returns portfolio summary: projects by status, budget vs actual, risk summary, resource utilization.
     */
    Map<String, Object> getSummary();

    /**
     * Returns resources assigned to multiple projects with overlapping dates.
     */
    List<Map<String, Object>> getResourceConflicts();
}
