package com.bank.updg.updg_resource.model.entity;

import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;

/**
 * Performance evaluation (F-506).
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
@TableName("pm_performance_eval")
public class PerformanceEval {

    @TableId
    private String evalId;

    private String staffId;

    private String evaluator;

    /** e.g. "2026-Q1" */
    private String evalPeriod;

    private Integer qualityScore;

    private Integer efficiencyScore;

    private Integer attitudeScore;

    private Integer skillScore;

    private Integer overallScore;

    private String comment;

    private LocalDateTime createTime;
}
