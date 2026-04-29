package com.bank.updg.updg_timesheet.service;

import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.bank.updg.updg_timesheet.model.entity.Timesheet;

import java.math.BigDecimal;
import java.time.LocalDate;
import java.util.List;

public interface TimesheetService {

    void submit(String staffId, String projectId, LocalDate workDate, BigDecimal hours, String remark);

    void approve(String timesheetId, boolean approved);

    Page<Timesheet> listByStaff(String staffId, int page, int size);

    Page<Timesheet> listByProject(String projectId, LocalDate from, LocalDate to, int page, int size);

    List<Timesheet> listPendingApproval();

    BigDecimal getTotalHours(String staffId, LocalDate from, LocalDate to);

    void batchApprove(List<String> timesheetIds, boolean approved);
}
