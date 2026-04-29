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
@TableName("pm_contract")
public class Contract {
    @TableId
    private String contractId;
    private String contractCode;
    private String contractName;
    private String contractType;
    private String partyA;
    private String partyB;
    private BigDecimal totalAmount;
    private String currency;
    private String signDate;
    private String startDate;
    private String endDate;
    private String projectId;
    private String status;
    private String createdBy;
    private String createTime;
    private String updateTime;
    private Integer reminderDays;
}
