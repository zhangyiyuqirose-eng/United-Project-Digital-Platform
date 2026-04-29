package com.bank.updg.updg_cost.controller;

import com.bank.updg.common.model.ApiResponse;
import com.bank.updg.updg_cost.service.CostAnalysisService;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

/**
 * Cost analysis endpoints.
 * F-209: Monthly cost trend data points.
 * F-210: Budget execution rate with category breakdown.
 */
@RestController
@RequestMapping("/api/cost")
@RequiredArgsConstructor
public class CostAnalysisController {

    private final CostAnalysisService costAnalysisService;

    /**
     * F-209: Get monthly cost trend for a project.
     */
    @GetMapping("/trend/{projectId}")
    public ApiResponse<List<Map<String, Object>>> getCostTrend(@PathVariable String projectId) {
        return ApiResponse.success(costAnalysisService.getMonthlyCostTrend(projectId));
    }

    /**
     * F-210: Get budget execution rate with per-category breakdown.
     */
    @GetMapping("/budget-execution/{projectId}")
    public ApiResponse<Map<String, Object>> getBudgetExecution(@PathVariable String projectId) {
        return ApiResponse.success(costAnalysisService.getBudgetExecutionRate(projectId));
    }
}
