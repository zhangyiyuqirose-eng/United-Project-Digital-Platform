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
 * Project risk register entry (F-306 风险识别与预警).
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
@TableName("pm_project_risk")
public class ProjectRisk {

    @TableId
    private String riskId;

    private String projectId;

    private String riskCode;

    private String title;

    private String description;

    /** CRITICAL, HIGH, MEDIUM, LOW */
    private String severity;

    /** SCHEDULE, COST, QUALITY, RESOURCE, COMPLIANCE, SECURITY */
    private String category;

    /** Probability 0.0-1.0 */
    private BigDecimal probability;

    /** Impact 1-5 */
    private Integer impact;

    /** Risk score = probability * impact */
    private BigDecimal riskScore;

    private String owner;

    /** IDENTIFIED, ASSESSED, MITIGATING, CLOSED, MATERIALIZED */
    private String status;

    private String mitigationPlan;

    private String contingencyPlan;

    private String identifiedBy;

    private LocalDateTime identifiedDate;

    private LocalDateTime closedDate;

    private LocalDateTime createTime;

    private LocalDateTime updateTime;
}
