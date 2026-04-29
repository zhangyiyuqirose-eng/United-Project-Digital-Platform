package com.bank.updg.updg_resource.model.entity;

import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDate;
import java.time.LocalDateTime;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
@TableName("pm_leave_request")
public class LeaveRequest {

    @TableId
    private String id;

    private String staffId;

    private String type; // ANNUAL, SICK, PERSONAL, OTHER

    private LocalDate startDate;

    private LocalDate endDate;

    private Integer days;

    private String reason;

    private String status; // PENDING, APPROVED, REJECTED

    private String approvedBy;

    private LocalDateTime approvedAt;
}
