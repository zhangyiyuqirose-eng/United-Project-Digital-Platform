package com.bank.updg.updg_timesheet.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.bank.updg.common.exception.BusinessException;
import com.bank.updg.common.model.enums.ErrorCodeEnum;
import com.bank.updg.updg_timesheet.mapper.TimesheetMapper;
import com.bank.updg.updg_timesheet.model.entity.Timesheet;
import com.bank.updg.updg_timesheet.service.AttendanceService;
import com.bank.updg.updg_timesheet.service.TimesheetService;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.math.BigDecimal;
import java.time.LocalDate;
import java.time.LocalDateTime;
import java.util.List;
import java.util.UUID;

@Service
@RequiredArgsConstructor
public class TimesheetServiceImpl implements TimesheetService {

    private static final BigDecimal MAX_DAILY_HOURS = new BigDecimal("8");

    private final TimesheetMapper timesheetMapper;
    private final AttendanceService attendanceService;

    @Override
    @Transactional
    public void submit(String staffId, String projectId, LocalDate workDate, BigDecimal hours, String remark) {
        if (hours.compareTo(MAX_DAILY_HOURS) > 0) {
            throw new BusinessException(ErrorCodeEnum.TIMESHEET_OVERFLOW);
        }

        String attendanceResult = attendanceService.compareWithAttendance(staffId, workDate, hours);

        Timesheet timesheet = Timesheet.builder()
                .timesheetId(UUID.randomUUID().toString().replace("-", ""))
                .staffId(staffId)
                .projectId(projectId)
                .workDate(workDate)
                .hours(hours)
                .checkStatus("PENDING")
                .attendanceCheckResult(attendanceResult)
                .remark(remark)
                .createTime(LocalDateTime.now())
                .updateTime(LocalDateTime.now())
                .build();
        timesheetMapper.insert(timesheet);
    }

    @Override
    public void approve(String timesheetId, boolean approved) {
        Timesheet timesheet = timesheetMapper.selectById(timesheetId);
        if (timesheet == null) {
            throw new BusinessException(ErrorCodeEnum.TIMESHEET_NOT_FOUND);
        }
        timesheet.setCheckStatus(approved ? "APPROVED" : "REJECTED");
        timesheet.setUpdateTime(LocalDateTime.now());
        timesheetMapper.updateById(timesheet);
    }

    @Override
    public Page<Timesheet> listByStaff(String staffId, int page, int size) {
        Page<Timesheet> pageObj = new Page<>(page, size);
        LambdaQueryWrapper<Timesheet> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(Timesheet::getStaffId, staffId)
               .orderByDesc(Timesheet::getWorkDate);
        return timesheetMapper.selectPage(pageObj, wrapper);
    }

    @Override
    public Page<Timesheet> listByProject(String projectId, LocalDate from, LocalDate to, int page, int size) {
        Page<Timesheet> pageObj = new Page<>(page, size);
        LambdaQueryWrapper<Timesheet> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(Timesheet::getProjectId, projectId);
        if (from != null) {
            wrapper.ge(Timesheet::getWorkDate, from);
        }
        if (to != null) {
            wrapper.le(Timesheet::getWorkDate, to);
        }
        wrapper.orderByDesc(Timesheet::getWorkDate);
        return timesheetMapper.selectPage(pageObj, wrapper);
    }

    @Override
    public List<Timesheet> listPendingApproval() {
        LambdaQueryWrapper<Timesheet> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(Timesheet::getCheckStatus, "PENDING")
               .orderByAsc(Timesheet::getWorkDate);
        return timesheetMapper.selectList(wrapper);
    }

    @Override
    public BigDecimal getTotalHours(String staffId, LocalDate from, LocalDate to) {
        LambdaQueryWrapper<Timesheet> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(Timesheet::getStaffId, staffId)
               .eq(Timesheet::getCheckStatus, "APPROVED");
        if (from != null) {
            wrapper.ge(Timesheet::getWorkDate, from);
        }
        if (to != null) {
            wrapper.le(Timesheet::getWorkDate, to);
        }
        List<Timesheet> list = timesheetMapper.selectList(wrapper);
        return list.stream()
                .map(Timesheet::getHours)
                .reduce(BigDecimal.ZERO, BigDecimal::add);
    }

    @Override
    @Transactional
    public void batchApprove(List<String> timesheetIds, boolean approved) {
        for (String id : timesheetIds) {
            approve(id, approved);
        }
    }
}
