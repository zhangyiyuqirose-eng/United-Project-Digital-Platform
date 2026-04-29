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
@TableName("pm_quality_defect")
public class QualityDefect {
    @TableId
    private String defectId;
    private String projectId;
    private String title;
    private String severity;
    private String type;
    private String source;
    private String status;
    private String reporter;
    private String assignee;
    private String description;
    private String foundDate;
    private String resolvedDate;
    private String fixVersion;
    private String relatedTask;
}
