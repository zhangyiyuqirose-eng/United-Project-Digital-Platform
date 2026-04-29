package com.bank.updg.updg_cost.service;

import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.bank.updg.updg_cost.model.entity.Cost;

import java.math.BigDecimal;
import java.time.LocalDateTime;

public interface CostService {

    /**
     * Collect cost from timesheet records: hours * rate.
     */
    void collectCostFromTimesheet(String projectId, LocalDateTime from, LocalDateTime to);

    Cost getCostByProject(String projectId);

    Page<Cost> listByProject(String projectId, int page, int size);

    /**
     * Calculate EVM metrics for a project.
     */
    void calculateEvm(String projectId);

    BigDecimal getTotalCost(String projectId);

    /**
     * Generate settlement statement for a project period.
     */
    void generateSettlement(String projectId, LocalDateTime from, LocalDateTime to);

    /**
     * F-206: Approve a settlement record.
     */
    void approveSettlement(String settlementId, String approvedBy);

    /**
     * F-206: Reject a settlement record with reason.
     */
    void rejectSettlement(String settlementId, String reason);
}
