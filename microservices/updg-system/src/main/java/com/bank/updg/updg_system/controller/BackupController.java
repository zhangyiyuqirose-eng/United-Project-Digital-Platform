package com.bank.updg.updg_system.controller;

import com.bank.updg.common.model.ApiResponse;
import com.bank.updg.updg_system.service.BackupService;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

/**
 * F-1410: Backup controller.
 */
@RestController
@RequestMapping("/api/system/backup")
@RequiredArgsConstructor
public class BackupController {

    private final BackupService backupService;

    @PostMapping("/trigger")
    public ApiResponse<String> triggerBackup(@RequestParam(defaultValue = "FULL") String type) {
        return ApiResponse.success(backupService.triggerBackup(type));
    }

    @GetMapping("/history")
    public ApiResponse<List<Map<String, Object>>> getHistory(
            @RequestParam(defaultValue = "10") int limit) {
        return ApiResponse.success(backupService.getHistory(limit));
    }

    @GetMapping("/{backupId}/status")
    public ApiResponse<Map<String, Object>> getStatus(@PathVariable String backupId) {
        return ApiResponse.success(backupService.getStatus(backupId));
    }

    @PostMapping("/{backupId}/cancel")
    public ApiResponse<Void> cancelBackup(@PathVariable String backupId) {
        backupService.cancelBackup(backupId);
        return ApiResponse.success();
    }
}