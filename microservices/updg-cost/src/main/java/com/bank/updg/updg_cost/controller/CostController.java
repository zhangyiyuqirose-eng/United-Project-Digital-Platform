package com.bank.updg.updg_cost.controller;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.bank.updg.common.model.ApiResponse;
import com.bank.updg.updg_cost.mapper.CostMapper;
import com.bank.updg.updg_cost.model.entity.Cost;
import com.bank.updg.updg_cost.service.CostService;
import lombok.RequiredArgsConstructor;
import org.springframework.format.annotation.DateTimeFormat;
import org.springframework.web.bind.annotation.*;

import java.time.LocalDateTime;
import java.util.List;

@RestController
@RequestMapping("/api/cost")
@RequiredArgsConstructor
public class CostController {

    private final CostService costService;
    private final CostMapper costMapper;

    @GetMapping("/list")
    public ApiResponse<Page<Cost>> listPage(
            @RequestParam(defaultValue = "1") int page,
            @RequestParam(defaultValue = "10") int limit,
            @RequestParam(required = false) String projectId) {
        Page<Cost> pageObj = new Page<>(page, limit);
        LambdaQueryWrapper<Cost> wrapper = new LambdaQueryWrapper<>();
        if (projectId != null) {
            wrapper.eq(Cost::getProjectId, projectId);
        }
        return ApiResponse.success(costMapper.selectPage(pageObj, wrapper));
    }

    @GetMapping
    public ApiResponse<List<Cost>> listAll() {
        return ApiResponse.success(costMapper.selectList(new LambdaQueryWrapper<>()));
    }

    @PostMapping("/collect")
    public ApiResponse collectCost(@RequestBody CostCollectRequest request) {
        costService.collectCostFromTimesheet(request.projectId, request.from, request.to);
        return ApiResponse.success("成本归集成功");
    }

    @GetMapping("/{projectId}")
    public ApiResponse getCostByProject(@PathVariable String projectId) {
        return ApiResponse.success(costService.getCostByProject(projectId));
    }

    @GetMapping("/{projectId}/list")
    public ApiResponse listByProject(@PathVariable String projectId,
                                     @RequestParam(defaultValue = "1") int page,
                                     @RequestParam(defaultValue = "20") int size) {
        return ApiResponse.success(costService.listByProject(projectId, page, size));
    }

    @PostMapping("/{projectId}/evm")
    public ApiResponse calculateEvm(@PathVariable String projectId) {
        costService.calculateEvm(projectId);
        return ApiResponse.success("EVM计算成功");
    }

    @GetMapping("/{projectId}/total")
    public ApiResponse getTotalCost(@PathVariable String projectId) {
        return ApiResponse.success(costService.getTotalCost(projectId));
    }

    @PostMapping("/{projectId}/settlement")
    public ApiResponse generateSettlement(@PathVariable String projectId,
                                          @RequestParam @DateTimeFormat(iso = DateTimeFormat.ISO.DATE_TIME) LocalDateTime from,
                                          @RequestParam @DateTimeFormat(iso = DateTimeFormat.ISO.DATE_TIME) LocalDateTime to) {
        costService.generateSettlement(projectId, from, to);
        return ApiResponse.success("结算单生成成功");
    }

    /**
     * F-206: Approve a settlement record.
     * Sets status to APPROVED and updates related contract payment records.
     */
    @PostMapping("/settlement/{id}/approve")
    public ApiResponse approveSettlement(@PathVariable String id,
                                         @RequestParam(required = false) String approvedBy) {
        costService.approveSettlement(id, approvedBy);
        return ApiResponse.success("结算单已审批");
    }

    /**
     * F-206: Reject a settlement record with reason.
     */
    @PostMapping("/settlement/{id}/reject")
    public ApiResponse rejectSettlement(@PathVariable String id,
                                        @RequestParam String reason) {
        costService.rejectSettlement(id, reason);
        return ApiResponse.success("结算单已拒绝");
    }

    static class CostCollectRequest {
        public String projectId;
        public LocalDateTime from;
        public LocalDateTime to;
    }
}
