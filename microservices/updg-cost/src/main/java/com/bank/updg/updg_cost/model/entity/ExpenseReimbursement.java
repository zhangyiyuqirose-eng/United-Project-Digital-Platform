package com.bank.updg.updg_cost.model.entity;

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
@TableName("pm_expense_reimbursement")
public class ExpenseReimbursement {

    @TableId
    private String id;

    private String staffId;

    private String projectId;

    private String type; // TRAVEL, MEAL, TRANSPORT, OTHER

    private BigDecimal amount;

    private Integer receiptCount;

    private String description;

    private String status; // DRAFT, SUBMITTED, APPROVED, REJECTED, PAID

    private LocalDateTime submittedAt;

    private LocalDateTime approvedAt;

    private LocalDateTime paidAt;
}
