package com.bank.updg.updg_project.controller;

import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.bank.updg.common.model.ApiResponse;
import com.bank.updg.updg_project.model.entity.ProgressAlert;
import com.bank.updg.updg_project.service.ProgressAlertService;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

import java.util.List;

/**
 * Progress alert endpoints (F-304).
 */
@RestController
@RequestMapping("/api/project")
@RequiredArgsConstructor
public class ProgressAlertController {

    private final ProgressAlertService progressAlertService;

    /**
     * Get all active progress alerts.
     */
    @GetMapping("/progress-alerts")
    public ApiResponse<List<ProgressAlert>> getActiveAlerts() {
        return ApiResponse.success(progressAlertService.getActiveAlerts());
    }

    /**
     * Check all active projects and generate alerts.
     */
    @PostMapping("/progress-alerts/check")
    public ApiResponse<List<ProgressAlert>> checkAllProjects() {
        return ApiResponse.success(progressAlertService.checkAllProjects());
    }

    /**
     * List alerts for a specific project.
     */
    @GetMapping("/progress-alerts/{projectId}")
    public ApiResponse<Page<ProgressAlert>> listByProject(
            @PathVariable String projectId,
            @RequestParam(defaultValue = "1") int page,
            @RequestParam(defaultValue = "10") int size) {
        return ApiResponse.success(progressAlertService.listByProject(projectId, page, size));
    }

    /**
     * Resolve a progress alert.
     */
    @PutMapping("/progress-alerts/{alertId}/resolve")
    public ApiResponse<Void> resolveAlert(@PathVariable String alertId) {
        progressAlertService.resolveAlert(alertId);
        return ApiResponse.success();
    }
}
