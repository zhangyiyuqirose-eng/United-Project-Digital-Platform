package com.bank.updg.updg_project.controller;

import com.bank.updg.common.model.ApiResponse;
import com.bank.updg.updg_project.service.PortfolioService;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

/**
 * F-601/F-603: Portfolio dashboard and resource conflict endpoints.
 */
@RestController
@RequestMapping("/api/project/portfolio")
@RequiredArgsConstructor
public class PortfolioController {

    private final PortfolioService portfolioService;

    /**
     * F-601: Get portfolio summary with projects by status, budget vs actual,
     * risk summary, and resource utilization rate.
     */
    @GetMapping("/summary")
    public ApiResponse<Map<String, Object>> summary() {
        return ApiResponse.success(portfolioService.getSummary());
    }

    /**
     * F-603: Get resources assigned to multiple projects with overlapping dates.
     */
    @GetMapping("/resource-conflicts")
    public ApiResponse<List<Map<String, Object>>> resourceConflicts() {
        return ApiResponse.success(portfolioService.getResourceConflicts());
    }
}
