package com.bank.updg.updg_project.model.entity;

import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.math.BigDecimal;
import java.time.LocalDateTime;

/**
 * Progress deviation alert (F-304).
 * Created when actual progress deviates from expected by > 15%.
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
@TableName("pm_progress_alert")
public class ProgressAlert {

    @TableId
    private String alertId;

    private String projectId;

    /** PROGRESS_DEVIATION */
    private String alertType;

    private String message;

    /** Actual progress percentage */
    private BigDecimal actualProgress;

    /** Expected progress percentage based on timeline */
    private BigDecimal expectedProgress;

    /** Deviation percentage */
    private BigDecimal deviation;

    /** WARNING, CRITICAL */
    private String severity;

    /** ACTIVE, ACKNOWLEDGED, RESOLVED */
    private String status;

    private String createdBy;

    private LocalDateTime createTime;

    private LocalDateTime ackTime;

    private LocalDateTime resolveTime;
}
