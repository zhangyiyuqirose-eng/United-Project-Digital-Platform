package com.bank.updg.updg_business.model.entity;

import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.math.BigDecimal;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
@TableName("pm_procurement_plan")
public class ProcurementPlan {
    @TableId
    private String planId;
    private String projectId;
    private String name;
    private String category;
    private BigDecimal estimatedCost;
    private String supplierId;
    private String requiredDate;
    private String status;
    private String priority;
    private String description;
    private String createdBy;
    private String createdAt;
    private String updatedAt;
}
