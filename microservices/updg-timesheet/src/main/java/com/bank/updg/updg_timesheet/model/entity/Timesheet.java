package com.bank.updg.updg_timesheet.model.entity;

import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.math.BigDecimal;
import java.time.LocalDate;
import java.time.LocalDateTime;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
@TableName("pm_timesheet")
public class Timesheet {

    @TableId
    private String timesheetId;

    private String staffId;

    private String projectId;

    private LocalDate workDate;

    private BigDecimal hours;

    private String checkStatus;

    private String attendanceCheckResult;

    private String remark;

    private LocalDateTime createTime;

    private LocalDateTime updateTime;
}
