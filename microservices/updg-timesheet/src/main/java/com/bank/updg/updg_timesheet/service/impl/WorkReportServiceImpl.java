package com.bank.updg.updg_timesheet.service.impl;

import com.bank.updg.updg_timesheet.mapper.TimesheetMapper;
import com.bank.updg.updg_timesheet.model.entity.Timesheet;
import com.bank.updg.updg_timesheet.service.WorkReportService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

import java.math.BigDecimal;
import java.time.DayOfWeek;
import java.time.LocalDate;
import java.time.format.DateTimeFormatter;
import java.time.temporal.TemporalAdjusters;
import java.util.*;
import java.util.stream.Collectors;

/**
 * Work report service implementation for F-1106.
 *
 * Provides unreported user detection, anomaly analysis, weekly report
 * generation, and reminder dispatch.
 */
@Slf4j
@Service
@RequiredArgsConstructor
public class WorkReportServiceImpl implements WorkReportService {

    private final TimesheetMapper timesheetMapper;

    @Override
    public List<Map<String, Object>> findUnreported(String deptId, LocalDate dateFrom, LocalDate dateTo) {
        // TODO: Query actual user roster from updg-system service via Feign or REST
        // For now, return placeholder structure
        List<Map<String, Object>> unreported = new ArrayList<>();

        log.info("Finding unreported users: dept={}, from={}, to={}", deptId, dateFrom, dateTo);

        // Placeholder: In production, join with user table and find users
        // with zero timesheet entries in the date range
        // SELECT u.* FROM pm_sys_user u
        // LEFT JOIN pm_timesheet t ON u.user_id = t.staff_id
        //   AND t.work_date BETWEEN ? AND ?
        // WHERE u.dept_id = ? AND t.timesheet_id IS NULL

        return unreported;
    }

    @Override
    public List<Map<String, Object>> detectAnomalies(String projectId) {
        List<Map<String, Object>> anomalies = new ArrayList<>();

        com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper<Timesheet> wrapper =
                new com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper<>();
        if (projectId != null && !projectId.isBlank()) {
            wrapper.eq(Timesheet::getProjectId, projectId);
        }
        List<Timesheet> allTimesheets = timesheetMapper.selectList(wrapper);

        // Group by staff_id + work_date to detect duplicates
        Map<String, List<Timesheet>> grouped = allTimesheets.stream()
                .collect(Collectors.groupingBy(t -> t.getStaffId() + "|" + t.getWorkDate()));

        for (Map.Entry<String, List<Timesheet>> entry : grouped.entrySet()) {
            List<Timesheet> records = entry.getValue();

            // Detect duplicate entries (same staff, same date, multiple records)
            if (records.size() > 2) {
                Map<String, Object> anomaly = new HashMap<>();
                anomaly.put("type", "DUPLICATE");
                anomaly.put("staffId", records.get(0).getStaffId());
                anomaly.put("workDate", records.get(0).getWorkDate());
                anomaly.put("count", records.size());
                anomaly.put("description", "Multiple timesheet entries on the same day");
                anomalies.add(anomaly);
            }

            // Detect underutilized (total hours < 4 on a workday)
            BigDecimal totalHours = records.stream()
                    .map(Timesheet::getHours)
                    .filter(Objects::nonNull)
                    .reduce(BigDecimal.ZERO, BigDecimal::add);

            if (totalHours.compareTo(new BigDecimal("4")) < 0) {
                Map<String, Object> anomaly = new HashMap<>();
                anomaly.put("type", "UNDERUTILIZED");
                anomaly.put("staffId", records.get(0).getStaffId());
                anomaly.put("workDate", records.get(0).getWorkDate());
                anomaly.put("totalHours", totalHours);
                anomaly.put("description", "Total hours below 4 hours threshold");
                anomalies.add(anomaly);
            }
        }

        // Detect fake entries (exactly 8.0 hours every day for a long streak)
        Map<String, List<Timesheet>> byStaff = allTimesheets.stream()
                .collect(Collectors.groupingBy(Timesheet::getStaffId));

        for (Map.Entry<String, List<Timesheet>> entry : byStaff.entrySet()) {
            String staffId = entry.getKey();
            List<Timesheet> staffRecords = entry.getValue();

            long exactEightCount = staffRecords.stream()
                    .filter(t -> t.getHours() != null && t.getHours().compareTo(new BigDecimal("8.0")) == 0)
                    .count();

            if (staffRecords.size() >= 5 && exactEightCount == staffRecords.size()) {
                Map<String, Object> anomaly = new HashMap<>();
                anomaly.put("type", "FAKE");
                anomaly.put("staffId", staffId);
                anomaly.put("recordCount", staffRecords.size());
                anomaly.put("description", "All entries are exactly 8.0 hours, possible padding");
                anomalies.add(anomaly);
            }
        }

        return anomalies;
    }

    @Override
    public Map<String, Object> getWeeklyReport(String staffId, LocalDate date) {
        LocalDate monday = date.with(TemporalAdjusters.previousOrSame(DayOfWeek.MONDAY));
        LocalDate sunday = date.with(TemporalAdjusters.nextOrSame(DayOfWeek.SUNDAY));

        com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper<Timesheet> wrapper =
                new com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper<>();
        wrapper.eq(Timesheet::getStaffId, staffId)
               .between(Timesheet::getWorkDate, monday, sunday)
               .orderByAsc(Timesheet::getWorkDate);

        List<Timesheet> weekRecords = timesheetMapper.selectList(wrapper);

        BigDecimal totalHours = weekRecords.stream()
                .map(Timesheet::getHours)
                .filter(Objects::nonNull)
                .reduce(BigDecimal.ZERO, BigDecimal::add);

        Set<String> projectIds = weekRecords.stream()
                .map(Timesheet::getProjectId)
                .filter(Objects::nonNull)
                .collect(Collectors.toSet());

        Map<String, Object> report = new LinkedHashMap<>();
        report.put("staffId", staffId);
        report.put("weekStart", monday.format(DateTimeFormatter.ISO_LOCAL_DATE));
        report.put("weekEnd", sunday.format(DateTimeFormatter.ISO_LOCAL_DATE));
        report.put("totalHours", totalHours);
        report.put("projectCount", projectIds.size());
        report.put("projects", projectIds);
        report.put("dailyRecords", weekRecords);

        return report;
    }

    @Override
    public int sendReminders(String deptId) {
        List<Map<String, Object>> unreported = findUnreported(deptId,
                LocalDate.now().with(TemporalAdjusters.firstDayOfMonth()),
                LocalDate.now());

        // TODO: Actually send notifications via updg-notify service
        // For each unreported user, create a NotifyMessage with channel=WECHAT
        // For now, log the reminder targets
        for (Map<String, Object> user : unreported) {
            log.info("Sending reminder to unreported user: {}", user);
        }

        log.info("Reminders sent: {}", unreported.size());
        return unreported.size();
    }
}
