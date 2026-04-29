package com.bank.updg.updg_cost.controller;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.bank.updg.common.model.ApiResponse;
import com.bank.updg.updg_cost.mapper.BudgetMapper;
import com.bank.updg.updg_cost.model.entity.Budget;
import com.bank.updg.updg_cost.service.BudgetService;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

import java.math.BigDecimal;
import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/cost/budget")
@RequiredArgsConstructor
public class BudgetController {

    private final BudgetService budgetService;
    private final BudgetMapper budgetMapper;

    @GetMapping("/list")
    public ApiResponse<Page<Budget>> listPage(
            @RequestParam(defaultValue = "1") int page,
            @RequestParam(defaultValue = "10") int limit) {
        Page<Budget> pageObj = new Page<>(page, limit);
        return ApiResponse.success(budgetMapper.selectPage(pageObj, new LambdaQueryWrapper<Budget>()));
    }

    @GetMapping
    public ApiResponse<List<Budget>> listAll() {
        return ApiResponse.success(budgetMapper.selectList(new LambdaQueryWrapper<Budget>()));
    }

    @PostMapping
    public ApiResponse<Budget> createBudget(@RequestBody Budget budget) {
        return ApiResponse.success(budgetService.createBudget(budget));
    }

    @PutMapping("/{id}")
    public ApiResponse<Void> updateBudget(@PathVariable String id, @RequestBody Budget budget) {
        budgetService.updateBudget(id, budget);
        return ApiResponse.success();
    }

    @GetMapping("/project/{projectId}")
    public ApiResponse<Budget> getBudget(@PathVariable String projectId) {
        return ApiResponse.success(budgetService.getBudget(projectId));
    }

    @GetMapping("/project/{projectId}/execution")
    public ApiResponse<Map<String, Object>> getBudgetExecution(@PathVariable String projectId) {
        return ApiResponse.success(budgetService.getBudgetExecution(projectId));
    }

    @PostMapping("/project/{projectId}/check")
    public ApiResponse<Boolean> checkBudget(@PathVariable String projectId,
                                            @RequestParam BigDecimal amount) {
        return ApiResponse.success(budgetService.checkBudget(projectId, amount));
    }
}
