package com.bank.updg.updg_resource.controller;

import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.bank.updg.common.model.ApiResponse;
import com.bank.updg.updg_resource.model.entity.PerformanceEval;
import com.bank.updg.updg_resource.service.PerformanceService;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

import java.util.Map;

@RestController
@RequestMapping("/api/resource/performance")
@RequiredArgsConstructor
public class PerformanceController {

    private final PerformanceService performanceService;

    @PostMapping
    public ApiResponse<PerformanceEval> createEval(@RequestBody PerformanceEval evalData) {
        return ApiResponse.success(performanceService.createEval(evalData));
    }

    @GetMapping("/staff/{staffId}")
    public ApiResponse<PerformanceEval> getEval(@PathVariable String staffId,
                                                @RequestParam(required = false) String period) {
        return ApiResponse.success(performanceService.getEval(staffId, period));
    }

    @GetMapping("/staff/{staffId}/history")
    public ApiResponse<Page<PerformanceEval>> getHistory(
            @PathVariable String staffId,
            @RequestParam(defaultValue = "1") int page,
            @RequestParam(defaultValue = "10") int size) {
        return ApiResponse.success(performanceService.listByStaff(staffId, page, size));
    }

    @GetMapping("/pool/{poolId}/avg")
    public ApiResponse<Map<String, Object>> getAvgScores(@PathVariable String poolId) {
        return ApiResponse.success(performanceService.getAvgScores(poolId));
    }
}
