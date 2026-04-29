package com.bank.updg.updg_cost.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.bank.updg.updg_cost.mapper.CostMapper;
import com.bank.updg.updg_cost.mapper.CostOutsourceMapper;
import com.bank.updg.updg_cost.model.entity.Cost;
import com.bank.updg.updg_cost.model.entity.CostOutsource;
import com.bank.updg.updg_cost.service.CostCalculationService;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.*;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
public class CostCalculationServiceImpl implements CostCalculationService {

    private final CostMapper costMapper;
    private final CostOutsourceMapper costOutsourceMapper;

    @Override
    @Transactional
    public BigDecimal calculateLaborCost(String projectId, LocalDateTime from, LocalDateTime to) {
        // In production, this would call updg-timesheet via Feign to get approved timesheets.
        // For now, query existing cost records of type LABOR for the project.

        // Calculate from existing LABOR cost records
        LambdaQueryWrapper<Cost> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(Cost::getProjectId, projectId)
                .eq(Cost::getCostType, "LABOR")
                .ge(Cost::getCalculateTime, from)
                .le(Cost::getCalculateTime, to);
        List<Cost> existingLaborCosts = costMapper.selectList(wrapper);

        BigDecimal totalLaborCost = existingLaborCosts.stream()
                .map(c -> c.getAmount() != null ? c.getAmount() : BigDecimal.ZERO)
                .reduce(BigDecimal.ZERO, BigDecimal::add);

        // If no existing labor costs, compute from outsource cost details
        if (totalLaborCost.compareTo(BigDecimal.ZERO) == 0) {
            // Query all outsource costs for this project (need to join with Cost to filter by projectId)
            List<CostOutsource> allOutsourceCosts = costOutsourceMapper.selectList(null);

            // Get cost IDs for this project
            LambdaQueryWrapper<Cost> costWrapper = new LambdaQueryWrapper<>();
            costWrapper.eq(Cost::getProjectId, projectId);
            List<Cost> projectCosts = costMapper.selectList(costWrapper);
            Set<String> projectCostIds = projectCosts.stream()
                    .map(Cost::getCostId)
                    .collect(Collectors.toSet());

            for (CostOutsource oc : allOutsourceCosts) {
                if (projectCostIds.contains(oc.getCostId()) && oc.getAmount() != null) {
                    totalLaborCost = totalLaborCost.add(oc.getAmount());
                }
            }
        }

        // Create aggregated labor cost record
        if (totalLaborCost.compareTo(BigDecimal.ZERO) > 0) {
            Cost laborCost = Cost.builder()
                    .costId(UUID.randomUUID().toString().replace("-", ""))
                    .projectId(projectId)
                    .costType("LABOR_CALCULATED")
                    .amount(totalLaborCost)
                    .calculateTime(LocalDateTime.now())
                    .build();
            costMapper.insert(laborCost);
        }

        return totalLaborCost;
    }

    @Override
    public List<Map<String, Object>> getLaborCostBreakdown(String projectId, LocalDateTime from, LocalDateTime to) {
        // Query outsource cost details grouped by staff
        LambdaQueryWrapper<Cost> costWrapper = new LambdaQueryWrapper<>();
        costWrapper.eq(Cost::getProjectId, projectId);
        List<Cost> projectCosts = costMapper.selectList(costWrapper);

        Set<String> projectCostIds = projectCosts.stream()
                .map(Cost::getCostId)
                .collect(Collectors.toSet());

        // Group by staff ID
        List<CostOutsource> allOutsource = costOutsourceMapper.selectList(null);
        Map<String, BigDecimal> byStaff = new HashMap<>();

        for (CostOutsource oc : allOutsource) {
            if (projectCostIds.contains(oc.getCostId()) && oc.getAmount() != null) {
                byStaff.merge(oc.getStaffId(), oc.getAmount(), BigDecimal::add);
            }
        }

        List<Map<String, Object>> result = new ArrayList<>();
        for (Map.Entry<String, BigDecimal> entry : byStaff.entrySet()) {
            Map<String, Object> item = new LinkedHashMap<>();
            item.put("staffId", entry.getKey());
            item.put("totalCost", entry.getValue());
            result.add(item);
        }

        return result;
    }

    @Override
    public BigDecimal calculateCompletedLaborCost(String projectId) {
        // Calculate labor cost from approved timesheets (for EVM earned value)
        LambdaQueryWrapper<Cost> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(Cost::getProjectId, projectId)
                .eq(Cost::getCostType, "LABOR");
        List<Cost> laborCosts = costMapper.selectList(wrapper);

        return laborCosts.stream()
                .map(c -> c.getAmount() != null ? c.getAmount() : BigDecimal.ZERO)
                .reduce(BigDecimal.ZERO, BigDecimal::add);
    }
}
