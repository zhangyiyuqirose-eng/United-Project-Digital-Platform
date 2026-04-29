package com.bank.updg.updg_cost.service;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.List;
import java.util.Map;

/**
 * Cost calculation service for labor cost auto-calculation.
 * F-202: Queries timesheet records, looks up resource hourly rates,
 * computes total labor cost, and creates cost records.
 */
public interface CostCalculationService {

    /**
     * Calculate labor cost from timesheet records for a project.
     * Queries approved timesheets, multiplies hours * hourly rate,
     * and creates cost records.
     */
    BigDecimal calculateLaborCost(String projectId, LocalDateTime from, LocalDateTime to);

    /**
     * Returns a breakdown of labor cost by resource.
     */
    List<Map<String, Object>> getLaborCostBreakdown(String projectId, LocalDateTime from, LocalDateTime to);

    /**
     * Calculate completed labor cost (approved timesheets only) for EVM.
     */
    BigDecimal calculateCompletedLaborCost(String projectId);
}
