package com.bank.updg.updg_timesheet.model.entity;

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
@TableName("pm_timesheet_attendance")
public class TimesheetAttendance {

    @TableId
    private String attendanceId;

    private String staffId;

    private LocalDate attendanceDate;

    private LocalDateTime checkInTime;

    private LocalDateTime checkOutTime;

    private LocalDateTime syncTime;
}
