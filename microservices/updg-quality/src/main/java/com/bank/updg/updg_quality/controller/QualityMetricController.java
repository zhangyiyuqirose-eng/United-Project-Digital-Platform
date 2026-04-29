package com.bank.updg.updg_quality.controller;

import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.bank.updg.common.model.ApiResponse;
import com.bank.updg.updg_quality.model.entity.QualityMetric;
import com.bank.updg.updg_quality.service.QualityService;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/quality/metric")
@RequiredArgsConstructor
public class QualityMetricController {

    private final QualityService qualityService;

    @PostMapping
    public ApiResponse<Void> recordMetric(
            @RequestParam String projectId,
            @RequestParam String metricName,
            @RequestParam Double value,
            @RequestParam(required = false) Double target,
            @RequestParam(required = false) String unit) {
        qualityService.recordMetric(projectId, metricName, value, target, unit);
        return ApiResponse.success();
    }

    @GetMapping("/project/{projectId}")
    public ApiResponse<Page<QualityMetric>> getMetrics(
            @PathVariable String projectId,
            @RequestParam(defaultValue = "1") int page,
            @RequestParam(defaultValue = "10") int size) {
        return ApiResponse.success(qualityService.getMetrics(projectId, page, size));
    }
}
