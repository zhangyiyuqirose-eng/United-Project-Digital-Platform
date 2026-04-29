package com.bank.updg.updg_cost.service;

import java.math.BigDecimal;
import java.util.List;
import java.util.Map;

/**
 * Cost analysis service for trend and budget execution metrics.
 * F-209: Monthly cost trend data points.
 * F-210: Budget execution rate with per-category breakdown.
 */
public interface CostAnalysisService {

    /**
     * Returns monthly cost data points for a project.
     * Each map contains: year, month, totalAmount, recordCount.
     */
    List<Map<String, Object>> getMonthlyCostTrend(String projectId);

    /**
     * Returns budget execution rate: actual cost / budget * 100,
     * with per-category breakdown (labor, outsource, procurement, other).
     */
    Map<String, Object> getBudgetExecutionRate(String projectId);
}
