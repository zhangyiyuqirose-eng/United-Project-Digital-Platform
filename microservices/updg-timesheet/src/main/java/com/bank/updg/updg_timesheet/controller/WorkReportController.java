package com.bank.updg.updg_timesheet.controller;

import com.bank.updg.common.model.ApiResponse;
import com.bank.updg.updg_timesheet.service.WorkReportService;
import lombok.RequiredArgsConstructor;
import org.springframework.format.annotation.DateTimeFormat;
import org.springframework.web.bind.annotation.*;

import java.time.LocalDate;
import java.util.List;
import java.util.Map;

/**
 * Work report management API (F-1106).
 *
 * Handles unreported user detection, timesheet anomaly analysis,
 * weekly report generation, and reminder dispatch.
 */
@RestController
@RequestMapping("/api/timesheet/report")
@RequiredArgsConstructor
public class WorkReportController {

    private final WorkReportService workReportService;

    /**
     * Find users who haven't submitted reports in the given date range.
     */
    @GetMapping("/unreported")
    public ApiResponse<List<Map<String, Object>>> findUnreported(
            @RequestParam(required = false) String deptId,
            @RequestParam(required = false) @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate dateFrom,
            @RequestParam(required = false) @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate dateTo) {

        if (dateFrom == null) {
            dateFrom = LocalDate.now().withDayOfMonth(1);
        }
        if (dateTo == null) {
            dateTo = LocalDate.now();
        }

        return ApiResponse.success(workReportService.findUnreported(deptId, dateFrom, dateTo));
    }

    /**
     * Detect timesheet anomalies: underutilized hours, duplicate entries,
     * and suspicious patterns (fake padding).
     */
    @GetMapping("/anomalies")
    public ApiResponse<List<Map<String, Object>>> detectAnomalies(
            @RequestParam(required = false) String projectId) {
        return ApiResponse.success(workReportService.detectAnomalies(projectId));
    }

    /**
     * Get weekly work report for a specific staff member.
     * The date parameter determines which week (Monday-Sunday).
     */
    @GetMapping("/staff/{staffId}/weekly")
    public ApiResponse<Map<String, Object>> getWeeklyReport(
            @PathVariable String staffId,
            @RequestParam @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate date) {
        return ApiResponse.success(workReportService.getWeeklyReport(staffId, date));
    }

    /**
     * Send reminders to all unreported users in a department.
     */
    @PostMapping("/remind")
    public ApiResponse<Integer> sendReminders(
            @RequestParam(required = false) String deptId) {
        int count = workReportService.sendReminders(deptId);
        return ApiResponse.success(count);
    }
}
