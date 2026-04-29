package com.bank.updg.updg_timesheet.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.bank.updg.updg_timesheet.mapper.TimesheetAttendanceMapper;
import com.bank.updg.updg_timesheet.model.entity.TimesheetAttendance;
import com.bank.updg.updg_timesheet.service.AttendanceService;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.math.BigDecimal;
import java.math.RoundingMode;
import java.time.Duration;
import java.time.LocalDate;
import java.time.LocalDateTime;
import java.util.List;
import java.util.UUID;

@Service
@RequiredArgsConstructor
public class AttendanceServiceImpl implements AttendanceService {

    private final TimesheetAttendanceMapper attendanceMapper;

    @Override
    public void syncAttendance(List<TimesheetAttendance> records) {
        for (TimesheetAttendance record : records) {
            if (record.getAttendanceId() == null) {
                record.setAttendanceId(UUID.randomUUID().toString().replace("-", ""));
            }
            if (record.getSyncTime() == null) {
                record.setSyncTime(LocalDateTime.now());
            }
            attendanceMapper.insert(record);
        }
    }

    @Override
    public List<TimesheetAttendance> getByStaffAndDate(String staffId, LocalDate from, LocalDate to) {
        LambdaQueryWrapper<TimesheetAttendance> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(TimesheetAttendance::getStaffId, staffId);
        if (from != null) {
            wrapper.ge(TimesheetAttendance::getAttendanceDate, from);
        }
        if (to != null) {
            wrapper.le(TimesheetAttendance::getAttendanceDate, to);
        }
        return attendanceMapper.selectList(wrapper);
    }

    @Override
    public String compareWithAttendance(String staffId, LocalDate workDate, BigDecimal reportedHours) {
        LambdaQueryWrapper<TimesheetAttendance> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(TimesheetAttendance::getStaffId, staffId)
               .eq(TimesheetAttendance::getAttendanceDate, workDate);
        List<TimesheetAttendance> records = attendanceMapper.selectList(wrapper);

        if (records.isEmpty() || records.get(0).getCheckInTime() == null || records.get(0).getCheckOutTime() == null) {
            return "MISMATCH";
        }

        TimesheetAttendance attendance = records.get(0);
        Duration duration = Duration.between(attendance.getCheckInTime(), attendance.getCheckOutTime());
        BigDecimal actualHours = BigDecimal.valueOf(duration.toMinutes())
                .divide(BigDecimal.valueOf(60), 2, RoundingMode.HALF_UP);

        // Allow 1-hour tolerance
        BigDecimal diff = actualHours.subtract(reportedHours).abs();
        return diff.compareTo(BigDecimal.ONE) <= 0 ? "MATCH" : "MISMATCH";
    }
}
