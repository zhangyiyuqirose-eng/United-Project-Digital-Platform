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
@TableName("pm_quotation")
public class Quotation {
    @TableId
    private String quotationId;
    private String opportunityId;
    private String projectId;
    private String quoteNumber;
    private BigDecimal totalPrice;
    private BigDecimal taxRate;
    private String validUntil;
    private String status;
    private String items;
    private String createdBy;
    private String createdAt;
    private String updatedAt;
}
