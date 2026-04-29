package com.bank.updg.updg_system.service;

import java.util.List;
import java.util.Map;

/**
 * F-1301: Dashboard analytics service.
 */
public interface DashboardService {

    /**
     * Get overview statistics for dashboard.
     */
    Map<String, Object> getOverview();

    /**
     * Get trend data for specified dimension.
     * @param dimension PROJECT, COST, RESOURCE, RISK
     * @param period DAY, WEEK, MONTH, QUARTER
     */
    List<Map<String, Object>> getTrend(String dimension, String period);

    /**
     * Get top risks across all projects.
     * @param limit max number of risks to return
     */
    List<Map<String, Object>> getTopRisks(int limit);
}