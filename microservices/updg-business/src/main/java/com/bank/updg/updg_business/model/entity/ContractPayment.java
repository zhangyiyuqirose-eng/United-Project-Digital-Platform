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
@TableName("pm_contract_payment")
public class ContractPayment {
    @TableId
    private String paymentId;
    private String contractId;
    private String milestoneName;
    private String triggerCondition;
    private BigDecimal amount;
    private String dueDate;
    private String actualDate;
    private String status;
    private String remark;
}
