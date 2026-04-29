package com.bank.updg.updg_cost.model.entity;

import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.math.BigDecimal;
import java.time.LocalDateTime;

/**
 * Budget management (F-201).
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
@TableName("pm_budget")
public class Budget {

    @TableId
    private String budgetId;

    private String projectId;

    private Integer budgetYear;

    private BigDecimal totalBudget;

    private BigDecimal laborBudget;

    private BigDecimal outsourceBudget;

    private BigDecimal procurementBudget;

    private BigDecimal otherBudget;

    private String approvedBy;

    private LocalDateTime approvedDate;

    /** DRAFT, APPROVED, ADJUSTED */
    private String status;

    private LocalDateTime createTime;

    private LocalDateTime updateTime;
}
