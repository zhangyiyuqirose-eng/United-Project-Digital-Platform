package com.bank.updg.updg_timesheet.service;

import com.bank.updg.updg_timesheet.model.entity.TimesheetAttendance;

import java.time.LocalDate;
import java.util.List;

public interface AttendanceService {

    void syncAttendance(List<TimesheetAttendance> records);

    List<TimesheetAttendance> getByStaffAndDate(String staffId, LocalDate from, LocalDate to);

    /**
     * Compare timesheet hours with attendance check-in/out records.
     * Returns "MATCH" if hours align, "MISMATCH" otherwise.
     */
    String compareWithAttendance(String staffId, LocalDate workDate, java.math.BigDecimal reportedHours);
}
