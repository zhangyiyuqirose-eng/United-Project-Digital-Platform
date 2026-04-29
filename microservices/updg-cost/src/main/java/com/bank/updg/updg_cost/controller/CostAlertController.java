package com.bank.updg.updg_cost.controller;

import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.bank.updg.common.model.ApiResponse;
import com.bank.updg.updg_cost.model.entity.CostAlert;
import com.bank.updg.updg_cost.service.CostAlertService;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/cost/alert")
@RequiredArgsConstructor
public class CostAlertController {

    private final CostAlertService costAlertService;

    @GetMapping("/project/{projectId}")
    public ApiResponse<Page<CostAlert>> listAlerts(
            @PathVariable String projectId,
            @RequestParam(required = false) String status,
            @RequestParam(defaultValue = "1") int page,
            @RequestParam(defaultValue = "10") int size) {
        return ApiResponse.success(costAlertService.listAlerts(projectId, status, page, size));
    }

    @GetMapping("/active")
    public ApiResponse<List<CostAlert>> getActiveAlerts() {
        return ApiResponse.success(costAlertService.getActiveAlerts());
    }

    @PostMapping("/check/{projectId}")
    public ApiResponse<List<CostAlert>> checkAlerts(@PathVariable String projectId) {
        return ApiResponse.success(costAlertService.checkCostAlerts(projectId));
    }

    @PutMapping("/{id}/acknowledge")
    public ApiResponse<Void> acknowledgeAlert(@PathVariable String id,
                                              @RequestParam String userId) {
        costAlertService.acknowledgeAlert(id, userId);
        return ApiResponse.success();
    }

    @PutMapping("/{id}/resolve")
    public ApiResponse<Void> resolveAlert(@PathVariable String id) {
        costAlertService.resolveAlert(id);
        return ApiResponse.success();
    }
}
