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
@TableName("pm_business_opportunity")
public class BusinessOpportunity {
    @TableId
    private String opportunityId;
    private String name;
    private String customerId;
    private String stage;
    private BigDecimal estimatedValue;
    private Integer probability;
    private String ownerId;
    private String expectedCloseDate;
    private String source;
    private String description;
    private String createdAt;
    private String updatedAt;
    private String projectId;
}
