package com.bank.updg.updg_report.controller;

import com.bank.updg.common.model.ApiResponse;
import com.bank.updg.updg_report.service.ReportService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;
import java.util.Map;

/**
 * Report generation controller.
 * Provides endpoints to generate and download Excel reports.
 */
@RestController
@RequestMapping("/api/report")
@RequiredArgsConstructor
public class ReportController {

    private final ReportService reportService;

    @GetMapping("/project/{projectId}/download")
    public ResponseEntity<byte[]> downloadProjectReport(
            @org.springframework.web.bind.annotation.PathVariable String projectId,
            @RequestParam(defaultValue = "xlsx") String format) {
        byte[] data = reportService.generateProjectReport(projectId, format);
        return buildDownloadResponse(data, "project-report-" + projectId);
    }

    @GetMapping("/cost/{projectId}/download")
    public ResponseEntity<byte[]> downloadCostReport(
            @org.springframework.web.bind.annotation.PathVariable String projectId,
            @RequestParam(defaultValue = "xlsx") String format) {
        byte[] data = reportService.generateCostReport(projectId, format);
        return buildDownloadResponse(data, "cost-report-" + projectId);
    }

    @GetMapping("/timesheet/download")
    public ResponseEntity<byte[]> downloadTimesheetReport(
            @RequestParam String staffId,
            @RequestParam(required = false) String month,
            @RequestParam(defaultValue = "xlsx") String format) {
        byte[] data = reportService.generateTimesheetReport(staffId, month, format);
        String monthSuffix = month != null ? "-" + month : "";
        return buildDownloadResponse(data, "timesheet-report-" + staffId + monthSuffix);
    }

    @GetMapping("/resource/download")
    public ResponseEntity<byte[]> downloadResourceReport(
            @RequestParam String poolId,
            @RequestParam(defaultValue = "xlsx") String format) {
        byte[] data = reportService.generateResourceReport(poolId, format);
        return buildDownloadResponse(data, "resource-report-" + poolId);
    }

    @GetMapping("/portfolio/download")
    public ResponseEntity<byte[]> downloadPortfolioReport(
            @RequestParam(defaultValue = "xlsx") String format) {
        byte[] data = reportService.generatePortfolioReport(format);
        return buildDownloadResponse(data, "portfolio-report");
    }

    @GetMapping("/list")
    public ApiResponse<List<Map<String, Object>>> listReports(
            @RequestParam(required = false) String type,
            @RequestParam(defaultValue = "1") int page,
            @RequestParam(defaultValue = "10") int size) {
        return ApiResponse.success(reportService.listReports(type, page, size));
    }

    private ResponseEntity<byte[]> buildDownloadResponse(byte[] data, String baseName) {
        String fileName = baseName + ".xlsx";
        return ResponseEntity.ok()
                .header(HttpHeaders.CONTENT_DISPOSITION, "attachment; filename=\"" + fileName + "\"")
                .contentType(MediaType.parseMediaType("application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"))
                .header(HttpHeaders.ACCESS_CONTROL_EXPOSE_HEADERS, HttpHeaders.CONTENT_DISPOSITION)
                .body(data);
    }
}
