package com.bank.updg.updg_cost.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.bank.updg.common.exception.BusinessException;
import com.bank.updg.common.model.enums.ErrorCodeEnum;
import com.bank.updg.updg_cost.mapper.BudgetMapper;
import com.bank.updg.updg_cost.mapper.CostMapper;
import com.bank.updg.updg_cost.model.entity.Budget;
import com.bank.updg.updg_cost.model.entity.Cost;
import com.bank.updg.updg_cost.service.CostAnalysisService;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.math.BigDecimal;
import java.math.RoundingMode;
import java.time.LocalDateTime;
import java.util.*;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
public class CostAnalysisServiceImpl implements CostAnalysisService {

    private final CostMapper costMapper;
    private final BudgetMapper budgetMapper;

    @Override
    public List<Map<String, Object>> getMonthlyCostTrend(String projectId) {
        LambdaQueryWrapper<Cost> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(Cost::getProjectId, projectId)
                .orderByAsc(Cost::getCalculateTime);
        List<Cost> costs = costMapper.selectList(wrapper);

        // Group by year-month
        Map<String, List<Cost>> grouped = costs.stream()
                .filter(c -> c.getCalculateTime() != null)
                .collect(Collectors.groupingBy(
                        c -> c.getCalculateTime().getYear() + "-" +
                                String.format("%02d", c.getCalculateTime().getMonthValue())
                ));

        List<Map<String, Object>> result = new ArrayList<>();
        for (Map.Entry<String, List<Cost>> entry : grouped.entrySet().stream()
                .sorted(Map.Entry.comparingByKey())
                .collect(Collectors.toList())) {
            String[] parts = entry.getKey().split("-");
            BigDecimal total = entry.getValue().stream()
                    .map(c -> c.getAmount() != null ? c.getAmount() : BigDecimal.ZERO)
                    .reduce(BigDecimal.ZERO, BigDecimal::add);

            Map<String, Object> point = new LinkedHashMap<>();
            point.put("year", Integer.parseInt(parts[0]));
            point.put("month", Integer.parseInt(parts[1]));
            point.put("totalAmount", total);
            point.put("recordCount", entry.getValue().size());
            result.add(point);
        }

        return result;
    }

    @Override
    public Map<String, Object> getBudgetExecutionRate(String projectId) {
        Budget budget = budgetMapper.selectOne(
                new LambdaQueryWrapper<Budget>()
                        .eq(Budget::getProjectId, projectId)
                        .orderByDesc(Budget::getCreateTime)
                        .last("LIMIT 1"));

        if (budget == null) {
            throw new BusinessException(ErrorCodeEnum.PARAM_ERROR, "No budget found for project: " + projectId);
        }

        // Get actual costs by type
        LambdaQueryWrapper<Cost> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(Cost::getProjectId, projectId);
        List<Cost> costs = costMapper.selectList(wrapper);

        Map<String, BigDecimal> actualByType = new HashMap<>();
        BigDecimal totalActual = BigDecimal.ZERO;

        for (Cost cost : costs) {
            String type = cost.getCostType() != null ? cost.getCostType() : "OTHER";
            BigDecimal amount = cost.getAmount() != null ? cost.getAmount() : BigDecimal.ZERO;
            actualByType.merge(type, amount, BigDecimal::add);
            totalActual = totalActual.add(amount);
        }

        BigDecimal totalBudget = budget.getTotalBudget() != null ? budget.getTotalBudget() : BigDecimal.ZERO;
        BigDecimal executionRate = totalBudget.compareTo(BigDecimal.ZERO) > 0
                ? totalActual.multiply(new BigDecimal("100")).divide(totalBudget, 2, RoundingMode.HALF_UP)
                : BigDecimal.ZERO;

        // Per-category breakdown
        Map<String, Object> categoryBreakdown = new LinkedHashMap<>();
        categoryBreakdown.put("labor", Map.of(
                "budget", budget.getLaborBudget() != null ? budget.getLaborBudget() : BigDecimal.ZERO,
                "actual", actualByType.getOrDefault("LABOR", BigDecimal.ZERO)));
        categoryBreakdown.put("outsource", Map.of(
                "budget", budget.getOutsourceBudget() != null ? budget.getOutsourceBudget() : BigDecimal.ZERO,
                "actual", actualByType.getOrDefault("OUTSOURCE", BigDecimal.ZERO)));
        categoryBreakdown.put("procurement", Map.of(
                "budget", budget.getProcurementBudget() != null ? budget.getProcurementBudget() : BigDecimal.ZERO,
                "actual", actualByType.getOrDefault("PROCUREMENT", BigDecimal.ZERO)));
        categoryBreakdown.put("other", Map.of(
                "budget", budget.getOtherBudget() != null ? budget.getOtherBudget() : BigDecimal.ZERO,
                "actual", actualByType.getOrDefault("OTHER", BigDecimal.ZERO)));

        Map<String, Object> result = new LinkedHashMap<>();
        result.put("projectId", projectId);
        result.put("totalBudget", totalBudget);
        result.put("totalActual", totalActual);
        result.put("executionRate", executionRate);
        result.put("variance", totalBudget.subtract(totalActual));
        result.put("categoryBreakdown", categoryBreakdown);
        return result;
    }
}
