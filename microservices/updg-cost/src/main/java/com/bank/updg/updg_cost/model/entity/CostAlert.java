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
 * Cost variance alert (F-204).
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
@TableName("pm_cost_alert")
public class CostAlert {

    @TableId
    private String alertId;

    private String projectId;

    /** BUDGET_OVER_RUN, CPI_LOW, SPI_LOW, VARIANCE_HIGH */
    private String alertType;

    /** WARNING, CRITICAL */
    private String severity;

    private String message;

    private BigDecimal currentValue;

    private BigDecimal threshold;

    /** ACTIVE, ACKNOWLEDGED, RESOLVED */
    private String status;

    private String createdBy;

    private LocalDateTime createTime;

    private LocalDateTime ackTime;

    private LocalDateTime resolveTime;
}
