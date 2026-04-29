package com.bank.updg.updg_project.model.entity;

import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.math.BigDecimal;
import java.time.LocalDate;
import java.time.LocalDateTime;

/**
 * Pre-initiation application (F-101).
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
@TableName("pm_pre_initiation")
public class PreInitiation {

    @TableId
    private String preId;

    private String projectCode;

    private String projectName;

    /** Business type */
    private String businessType;

    /** Applicant user ID */
    private String applicant;

    private String deptId;

    private String description;

    private BigDecimal expectedBudget;

    private LocalDate expectedStart;

    private LocalDate expectedEnd;

    /** LOW, MEDIUM, HIGH, CRITICAL */
    private String priority;

    /** DRAFT, SUBMITTED, APPROVED, REJECTED */
    private String status;

    private LocalDateTime submitTime;

    private LocalDateTime approveTime;

    private LocalDateTime createTime;

    private LocalDateTime updateTime;
}
