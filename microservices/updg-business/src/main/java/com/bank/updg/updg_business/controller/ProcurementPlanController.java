package com.bank.updg.updg_business.controller;

import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.bank.updg.common.model.ApiResponse;
import com.bank.updg.updg_business.model.entity.ProcurementPlan;
import com.bank.updg.updg_business.service.ProcurementPlanService;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/business/procurement-plan")
@RequiredArgsConstructor
public class ProcurementPlanController {

    private final ProcurementPlanService procurementPlanService;

    @PostMapping
    public ApiResponse<ProcurementPlan> create(@RequestBody ProcurementPlan data) {
        return ApiResponse.success(procurementPlanService.createPlan(data));
    }

    @PutMapping("/{id}")
    public ApiResponse<Void> update(@PathVariable String id, @RequestBody ProcurementPlan data) {
        procurementPlanService.updatePlan(id, data);
        return ApiResponse.success();
    }

    @GetMapping("/{id}")
    public ApiResponse<ProcurementPlan> getDetail(@PathVariable String id) {
        return ApiResponse.success(procurementPlanService.getPlan(id));
    }

    @GetMapping("/list")
    public ApiResponse<Page<ProcurementPlan>> list(
            @RequestParam(required = false) String projectId,
            @RequestParam(required = false) String status,
            @RequestParam(defaultValue = "1") int page,
            @RequestParam(defaultValue = "10") int size) {
        return ApiResponse.success(procurementPlanService.listPlans(projectId, status, page, size));
    }

    @GetMapping("/project/{projectId}")
    public ApiResponse<List<ProcurementPlan>> getByProject(@PathVariable String projectId) {
        return ApiResponse.success(procurementPlanService.getByProjectId(projectId));
    }

    @GetMapping("/overdue")
    public ApiResponse<List<ProcurementPlan>> getOverdue() {
        return ApiResponse.success(procurementPlanService.getOverdue());
    }
}
