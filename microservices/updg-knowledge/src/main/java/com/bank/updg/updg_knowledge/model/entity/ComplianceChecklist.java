package com.bank.updg.updg_knowledge.model.entity;

import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.math.BigDecimal;
import java.time.LocalDateTime;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
@TableName("pm_compliance_checklist")
public class ComplianceChecklist {

    @TableId
    private String id;

    private String projectId;

    private String category;

    private String items; // JSON

    private String completedItems; // JSON

    private BigDecimal completionRate;

    private String checkedBy;

    private LocalDateTime checkedAt;
}
