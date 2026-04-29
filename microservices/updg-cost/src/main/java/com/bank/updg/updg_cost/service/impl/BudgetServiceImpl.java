package com.bank.updg.updg_cost.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.bank.updg.common.exception.BusinessException;
import com.bank.updg.common.model.enums.ErrorCodeEnum;
import com.bank.updg.updg_cost.mapper.BudgetMapper;
import com.bank.updg.updg_cost.mapper.CostMapper;
import com.bank.updg.updg_cost.model.entity.Budget;
import com.bank.updg.updg_cost.model.entity.Cost;
import com.bank.updg.updg_cost.service.BudgetService;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.UUID;

@Service
@RequiredArgsConstructor
public class BudgetServiceImpl implements BudgetService {

    private final BudgetMapper budgetMapper;
    private final CostMapper costMapper;

    @Override
    public Budget createBudget(Budget budgetData) {
        budgetData.setBudgetId(UUID.randomUUID().toString().replace("-", ""));
        budgetData.setStatus("DRAFT");
        budgetData.setCreateTime(LocalDateTime.now());
        budgetData.setUpdateTime(LocalDateTime.now());
        budgetMapper.insert(budgetData);
        return budgetData;
    }

    @Override
    public void updateBudget(String budgetId, Budget data) {
        Budget existing = budgetMapper.selectById(budgetId);
        if (existing == null) {
            throw new BusinessException(ErrorCodeEnum.PARAM_ERROR, "Budget not found: " + budgetId);
        }
        if ("APPROVED".equals(existing.getStatus())) {
            // When updating an approved budget, mark as ADJUSTED
            existing.setStatus("ADJUSTED");
        }
        if (data.getTotalBudget() != null) existing.setTotalBudget(data.getTotalBudget());
        if (data.getLaborBudget() != null) existing.setLaborBudget(data.getLaborBudget());
        if (data.getOutsourceBudget() != null) existing.setOutsourceBudget(data.getOutsourceBudget());
        if (data.getProcurementBudget() != null) existing.setProcurementBudget(data.getProcurementBudget());
        if (data.getOtherBudget() != null) existing.setOtherBudget(data.getOtherBudget());
        existing.setUpdateTime(LocalDateTime.now());
        budgetMapper.updateById(existing);
    }

    @Override
    public Budget getBudget(String projectId) {
        return budgetMapper.selectOne(
                new LambdaQueryWrapper<Budget>()
                        .eq(Budget::getProjectId, projectId)
                        .orderByDesc(Budget::getCreateTime)
                        .last("LIMIT 1"));
    }

    @Override
    public Map<String, Object> getBudgetExecution(String projectId) {
        Budget budget = getBudget(projectId);
        if (budget == null) {
            throw new BusinessException(ErrorCodeEnum.PARAM_ERROR, "No budget found for project: " + projectId);
        }

        // Calculate actual costs from cost table
        List<Cost> costs = costMapper.selectList(
                new LambdaQueryWrapper<Cost>()
                        .eq(Cost::getProjectId, projectId));

        BigDecimal actualTotal = costs.stream()
                .map(Cost::getAmount)
                .filter(a -> a != null)
                .reduce(BigDecimal.ZERO, BigDecimal::add);

        BigDecimal totalBudget = budget.getTotalBudget() != null ? budget.getTotalBudget() : BigDecimal.ZERO;
        BigDecimal variance = totalBudget.subtract(actualTotal);
        BigDecimal executionRate = totalBudget.compareTo(BigDecimal.ZERO) > 0
                ? actualTotal.multiply(new BigDecimal("100")).divide(totalBudget, 2, BigDecimal.ROUND_HALF_UP)
                : BigDecimal.ZERO;

        Map<String, Object> result = new HashMap<>();
        result.put("projectId", projectId);
        result.put("totalBudget", totalBudget);
        result.put("laborBudget", budget.getLaborBudget());
        result.put("outsourceBudget", budget.getOutsourceBudget());
        result.put("procurementBudget", budget.getProcurementBudget());
        result.put("otherBudget", budget.getOtherBudget());
        result.put("actualCost", actualTotal);
        result.put("variance", variance);
        result.put("executionRate", executionRate);
        result.put("status", budget.getStatus());
        return result;
    }

    @Override
    public boolean checkBudget(String projectId, BigDecimal amount) {
        Budget budget = getBudget(projectId);
        if (budget == null) {
            return false;
        }

        // Calculate current actual costs
        List<Cost> costs = costMapper.selectList(
                new LambdaQueryWrapper<Cost>()
                        .eq(Cost::getProjectId, projectId));

        BigDecimal actualTotal = costs.stream()
                .map(Cost::getAmount)
                .filter(a -> a != null)
                .reduce(BigDecimal.ZERO, BigDecimal::add);

        BigDecimal totalBudget = budget.getTotalBudget() != null ? budget.getTotalBudget() : BigDecimal.ZERO;
        BigDecimal remaining = totalBudget.subtract(actualTotal);

        return amount != null && remaining.compareTo(amount) >= 0;
    }
}
