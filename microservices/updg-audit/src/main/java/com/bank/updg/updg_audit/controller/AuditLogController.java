package com.bank.updg.updg_audit.controller;

import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.bank.updg.common.model.ApiResponse;
import com.bank.updg.updg_audit.model.entity.AuditLogEntry;
import com.bank.updg.updg_audit.service.AuditLogService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/audit/log")
@RequiredArgsConstructor
public class AuditLogController {

    private final AuditLogService auditLogService;

    @GetMapping
    public ApiResponse<Page<AuditLogEntry>> getLogsByUser(
            @RequestParam String userId,
            @RequestParam(defaultValue = "1") int page,
            @RequestParam(defaultValue = "10") int size) {
        return ApiResponse.success(auditLogService.getLogsByUser(userId, page, size));
    }

    @GetMapping("/module")
    public ApiResponse<Page<AuditLogEntry>> getLogsByModule(
            @RequestParam String module,
            @RequestParam(defaultValue = "1") int page,
            @RequestParam(defaultValue = "10") int size) {
        return ApiResponse.success(auditLogService.getLogsByModule(module, page, size));
    }

    @GetMapping("/action")
    public ApiResponse<Page<AuditLogEntry>> getLogsByAction(
            @RequestParam String action,
            @RequestParam(defaultValue = "1") int page,
            @RequestParam(defaultValue = "10") int size) {
        return ApiResponse.success(auditLogService.getLogsByAction(action, page, size));
    }

    @GetMapping("/range")
    public ApiResponse<Page<AuditLogEntry>> getLogsByDateRange(
            @RequestParam String from,
            @RequestParam String to,
            @RequestParam(defaultValue = "1") int page,
            @RequestParam(defaultValue = "10") int size) {
        return ApiResponse.success(auditLogService.getLogsByDateRange(from, to, page, size));
    }

    @GetMapping("/{logId}")
    public ApiResponse<AuditLogEntry> getLogDetail(@PathVariable String logId) {
        return ApiResponse.success(auditLogService.getLogDetail(logId));
    }

    @GetMapping("/export")
    public ResponseEntity<byte[]> exportLogs(
            @RequestParam(required = false) String userId,
            @RequestParam(required = false) String module,
            @RequestParam(required = false) String from,
            @RequestParam(required = false) String to) {
        byte[] csvData = auditLogService.exportLogs(userId, module, from, to);
        return ResponseEntity.ok()
                .header(HttpHeaders.CONTENT_DISPOSITION, "attachment; filename=audit_logs.csv")
                .contentType(MediaType.parseMediaType("text/csv"))
                .body(csvData);
    }
}
