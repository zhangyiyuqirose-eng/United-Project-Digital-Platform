package com.bank.updg.updg_quality.controller;

import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.bank.updg.common.model.ApiResponse;
import com.bank.updg.updg_quality.model.entity.QualityDefect;
import com.bank.updg.updg_quality.service.QualityService;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

import java.util.Map;

@RestController
@RequestMapping("/api/quality/defect")
@RequiredArgsConstructor
public class QualityDefectController {

    private final QualityService qualityService;

    @PostMapping
    public ApiResponse<QualityDefect> createDefect(@RequestBody QualityDefect defectData) {
        return ApiResponse.success(qualityService.createDefect(defectData));
    }

    @PutMapping("/{defectId}")
    public ApiResponse<Void> updateDefect(
            @PathVariable String defectId,
            @RequestParam(required = false) String status,
            @RequestParam(required = false) String assignee,
            @RequestParam(required = false) String fixVersion) {
        qualityService.updateDefect(defectId, status, assignee, fixVersion);
        return ApiResponse.success();
    }

    @GetMapping("/project/{projectId}")
    public ApiResponse<Page<QualityDefect>> getDefectsByProject(
            @PathVariable String projectId,
            @RequestParam(required = false) String status,
            @RequestParam(defaultValue = "1") int page,
            @RequestParam(defaultValue = "10") int size) {
        return ApiResponse.success(qualityService.getDefectsByProject(projectId, status, page, size));
    }

    @GetMapping("/{defectId}")
    public ApiResponse<QualityDefect> getDefectDetail(@PathVariable String defectId) {
        return ApiResponse.success(qualityService.getDefectDetail(defectId));
    }

    @PutMapping("/{defectId}/close")
    public ApiResponse<Void> closeDefect(@PathVariable String defectId) {
        qualityService.closeDefect(defectId);
        return ApiResponse.success();
    }

    @GetMapping("/project/{projectId}/stats")
    public ApiResponse<Map<String, Object>> getDefectStats(@PathVariable String projectId) {
        return ApiResponse.success(qualityService.getDefectStats(projectId));
    }
}
