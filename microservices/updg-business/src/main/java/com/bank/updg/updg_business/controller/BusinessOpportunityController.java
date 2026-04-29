package com.bank.updg.updg_business.controller;

import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.bank.updg.common.model.ApiResponse;
import com.bank.updg.updg_business.model.entity.BusinessOpportunity;
import com.bank.updg.updg_business.service.BusinessOpportunityService;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/business/opportunity")
@RequiredArgsConstructor
public class BusinessOpportunityController {

    private final BusinessOpportunityService opportunityService;

    @PostMapping
    public ApiResponse<BusinessOpportunity> create(@RequestBody BusinessOpportunity data) {
        return ApiResponse.success(opportunityService.createOpportunity(data));
    }

    @PutMapping("/{id}")
    public ApiResponse<Void> update(@PathVariable String id, @RequestBody Map<String, Object> data) {
        opportunityService.updateOpportunity(id, data);
        return ApiResponse.success();
    }

    @GetMapping("/{id}")
    public ApiResponse<BusinessOpportunity> getDetail(@PathVariable String id) {
        return ApiResponse.success(opportunityService.getOpportunity(id));
    }

    @GetMapping("/list")
    public ApiResponse<Page<BusinessOpportunity>> list(
            @RequestParam(required = false) String customerId,
            @RequestParam(required = false) String stage,
            @RequestParam(defaultValue = "1") int page,
            @RequestParam(defaultValue = "10") int size) {
        return ApiResponse.success(opportunityService.listOpportunities(customerId, stage, page, size));
    }

    @PostMapping("/{id}/advance-stage")
    public ApiResponse<Void> advanceStage(
            @PathVariable String id,
            @RequestParam String nextStage) {
        opportunityService.advanceStage(id, nextStage);
        return ApiResponse.success();
    }

    @GetMapping("/pipeline")
    public ApiResponse<List<Map<String, Object>>> getPipeline() {
        return ApiResponse.success(opportunityService.getPipeline());
    }
}
