package com.bank.updg.updg_quality.model.entity;

import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
@TableName("pm_quality_metric")
public class QualityMetric {
    @TableId
    private String metricId;
    private String projectId;
    private String metricName;
    private Double value;
    private Double target;
    private String unit;
    private String measuredDate;
}
