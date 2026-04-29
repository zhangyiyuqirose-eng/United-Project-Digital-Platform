package com.bank.updg.updg_system.controller;

import com.bank.updg.common.model.ApiResponse;
import com.bank.updg.updg_system.service.DashboardService;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

/**
 * F-1301: Dashboard analytics controller.
 */
@RestController
@RequestMapping("/api/dashboard")
@RequiredArgsConstructor
public class DashboardController {

    private final DashboardService dashboardService;

    @GetMapping("/overview")
    public ApiResponse<Map<String, Object>> getOverview() {
        return ApiResponse.success(dashboardService.getOverview());
    }

    @GetMapping("/trend")
    public ApiResponse<List<Map<String, Object>>> getTrend(
            @RequestParam String dimension,
            @RequestParam(defaultValue = "DAY") String period) {
        return ApiResponse.success(dashboardService.getTrend(dimension, period));
    }

    @GetMapping("/top-risks")
    public ApiResponse<List<Map<String, Object>>> getTopRisks(
            @RequestParam(defaultValue = "10") int limit) {
        return ApiResponse.success(dashboardService.getTopRisks(limit));
    }
}