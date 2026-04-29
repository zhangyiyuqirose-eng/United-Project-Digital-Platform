package com.bank.updg.updg_report.service;

import java.util.List;
import java.util.Map;

/**
 * Report generation service
 */
public interface ReportService {

    /**
     * Generate project report as Excel bytes
     *
     * @param projectId project identifier
     * @param format    output format (xlsx)
     * @return Excel file as byte array
     */
    byte[] generateProjectReport(String projectId, String format);

    /**
     * Generate cost report as Excel bytes
     *
     * @param projectId project identifier
     * @param format    output format (xlsx)
     * @return Excel file as byte array
     */
    byte[] generateCostReport(String projectId, String format);

    /**
     * Generate timesheet report as Excel bytes
     *
     * @param staffId staff identifier
     * @param month   report month (YYYY-MM)
     * @param format  output format (xlsx)
     * @return Excel file as byte array
     */
    byte[] generateTimesheetReport(String staffId, String month, String format);

    /**
     * Generate resource pool report as Excel bytes
     *
     * @param poolId resource pool identifier
     * @param format output format (xlsx)
     * @return Excel file as byte array
     */
    byte[] generateResourceReport(String poolId, String format);

    /**
     * Generate portfolio-level summary report as Excel bytes
     *
     * @param format output format (xlsx)
     * @return Excel file as byte array
     */
    byte[] generatePortfolioReport(String format);

    /**
     * List report metadata with pagination
     *
     * @param type report type filter
     * @param page page number (1-based)
     * @param size page size
     * @return list of report metadata maps
     */
    List<Map<String, Object>> listReports(String type, int page, int size);
}
