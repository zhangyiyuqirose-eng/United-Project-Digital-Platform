package com.bank.updg.updg_timesheet.service;

import java.time.LocalDate;
import java.util.List;
import java.util.Map;

/**
 * Work report management service for F-1106.
 * Handles unreported user detection, anomaly analysis, weekly reports, and reminders.
 */
public interface WorkReportService {

    /**
     * Find users who haven't submitted reports in the given date range.
     *
     * @param deptId    department filter (null = all departments)
     * @param dateFrom  start date
     * @param dateTo    end date
     * @return list of unreported user records
     */
    List<Map<String, Object>> findUnreported(String deptId, LocalDate dateFrom, LocalDate dateTo);

    /**
     * Detect timesheet anomalies for a project.
     *
     * @param projectId project ID (null = all projects)
     * @return list of anomaly records with type and description
     */
    List<Map<String, Object>> detectAnomalies(String projectId);

    /**
     * Get weekly work report for a specific staff member.
     *
     * @param staffId staff ID
     * @param date    any date within the target week (Monday-Sunday)
     * @return weekly report summary
     */
    Map<String, Object> getWeeklyReport(String staffId, LocalDate date);

    /**
     * Send reminders to unreported users in a department.
     *
     * @param deptId department ID
     * @return number of reminders sent
     */
    int sendReminders(String deptId);
}
