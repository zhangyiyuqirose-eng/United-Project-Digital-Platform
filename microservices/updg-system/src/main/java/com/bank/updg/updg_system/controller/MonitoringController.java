package com.bank.updg.updg_system.controller;

import com.bank.updg.common.model.ApiResponse;
import com.bank.updg.updg_system.service.MonitoringService;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

import java.util.Map;

/**
 * F-1411: Monitoring controller.
 */
@RestController
@RequestMapping("/api/system/monitor")
@RequiredArgsConstructor
public class MonitoringController {

    private final MonitoringService monitoringService;

    @GetMapping("/health")
    public ApiResponse<Map<String, Object>> checkHealth() {
        return ApiResponse.success(monitoringService.checkHealth());
    }

    @GetMapping("/metrics")
    public ApiResponse<Map<String, Object>> getMetrics() {
        return ApiResponse.success(monitoringService.getMetrics());
    }

    @GetMapping("/service/{serviceName}")
    public ApiResponse<Map<String, Object>> checkServiceStatus(@PathVariable String serviceName) {
        return ApiResponse.success(monitoringService.checkServiceStatus(serviceName));
    }

    @GetMapping("/alerts")
    public ApiResponse<Map<String, Object>> getAlertHistory(
            @RequestParam(defaultValue = "10") int limit) {
        return ApiResponse.success(monitoringService.getAlertHistory(limit));
    }
}