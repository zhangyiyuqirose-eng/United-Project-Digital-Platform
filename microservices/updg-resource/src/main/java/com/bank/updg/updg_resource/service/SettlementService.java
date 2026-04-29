package com.bank.updg.updg_resource.service;

import java.math.BigDecimal;
import java.util.Map;

public interface SettlementService {

    /**
     * Generate monthly settlement for a project.
     * Queries approved timesheets for the month, computes hours * rate,
     * creates settlement records.
     */
    Map<String, Object> generateMonthlySettlement(String projectId, String yearMonth);

    /**
     * Get monthly summary for a project.
     * Returns total hours, total cost, headcount.
     */
    Map<String, Object> getMonthlySummary(String projectId, String yearMonth);
}
