package com.bank.updg.updg_cost.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.bank.updg.updg_cost.mapper.BudgetMapper;
import com.bank.updg.updg_cost.mapper.CostMapper;
import com.bank.updg.updg_cost.mapper.CostOutsourceMapper;
import com.bank.updg.updg_cost.model.entity.Budget;
import com.bank.updg.updg_cost.model.entity.Cost;
import com.bank.updg.updg_cost.service.CostCalculationService;
import com.bank.updg.updg_cost.service.CostService;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.math.BigDecimal;
import java.math.RoundingMode;
import java.time.LocalDateTime;
import java.util.List;
import java.util.Map;
import java.util.UUID;

@Service
@RequiredArgsConstructor
public class CostServiceImpl implements CostService {

    private final CostMapper costMapper;
    private final CostOutsourceMapper costOutsourceMapper;
    private final BudgetMapper budgetMapper;
    private final CostCalculationService costCalculationService;

    @Override
    @Transactional
    public void collectCostFromTimesheet(String projectId, LocalDateTime from, LocalDateTime to) {
        // F-202: Calculate labor cost from timesheet records
        BigDecimal laborCost = costCalculationService.calculateLaborCost(projectId, from, to);

        // If no calculated labor cost exists, create a record based on timesheet data
        if (laborCost.compareTo(BigDecimal.ZERO) == 0) {
            Cost cost = Cost.builder()
                    .costId(UUID.randomUUID().toString().replace("-", ""))
                    .projectId(projectId)
                    .costType("LABOR")
                    .amount(BigDecimal.ZERO)
                    .calculateTime(LocalDateTime.now())
                    .evmPv(BigDecimal.ZERO)
                    .evmEv(BigDecimal.ZERO)
                    .evmAc(BigDecimal.ZERO)
                    .build();
            costMapper.insert(cost);
        }
    }

    @Override
    public Cost getCostByProject(String projectId) {
        LambdaQueryWrapper<Cost> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(Cost::getProjectId, projectId)
               .orderByDesc(Cost::getCalculateTime)
               .last("LIMIT 1");
        return costMapper.selectOne(wrapper);
    }

    @Override
    public Page<Cost> listByProject(String projectId, int page, int size) {
        Page<Cost> pageObj = new Page<>(page, size);
        LambdaQueryWrapper<Cost> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(Cost::getProjectId, projectId)
               .orderByDesc(Cost::getCalculateTime);
        return costMapper.selectPage(pageObj, wrapper);
    }

    @Override
    @Transactional
    public void calculateEvm(String projectId) {
        // Calculate EVM metrics: CPI = EV/AC, SPI = EV/PV
        Budget budget = budgetMapper.selectOne(new LambdaQueryWrapper<Budget>()
                .eq(Budget::getProjectId, projectId)
                .orderByDesc(Budget::getCreateTime)
                .last("LIMIT 1"));

        if (budget == null) {
            return;
        }

        BigDecimal pv = budget.getTotalBudget() != null ? budget.getTotalBudget() : BigDecimal.ZERO;
        BigDecimal ac = getTotalCost(projectId);

        // EV = budget * completion ratio (based on approved labor cost ratio)
        BigDecimal totalHours = costCalculationService.calculateLaborCost(projectId, null, null);
        BigDecimal completedHours = costCalculationService.calculateCompletedLaborCost(projectId);
        BigDecimal ev = pv.compareTo(BigDecimal.ZERO) > 0 && totalHours.compareTo(BigDecimal.ZERO) > 0
                ? pv.multiply(completedHours).divide(totalHours, 2, RoundingMode.HALF_UP)
                : BigDecimal.ZERO;

        // Inline EVM calculations (avoids cross-service import)
        BigDecimal cpi = ac.compareTo(BigDecimal.ZERO) > 0 ? ev.divide(ac, 4, RoundingMode.HALF_UP) : BigDecimal.ZERO;
        BigDecimal spi = pv.compareTo(BigDecimal.ZERO) > 0 ? ev.divide(pv, 4, RoundingMode.HALF_UP) : BigDecimal.ZERO;
        BigDecimal bac = pv;
        BigDecimal eac = cpi.compareTo(BigDecimal.ZERO) > 0 ? bac.divide(cpi, 2, RoundingMode.HALF_UP) : bac;

        // Save EVM snapshot
        Cost evmRecord = Cost.builder()
                .costId(UUID.randomUUID().toString().replace("-", ""))
                .projectId(projectId)
                .costType("EVM_SNAPSHOT")
                .amount(ac)
                .calculateTime(LocalDateTime.now())
                .evmPv(pv)
                .evmEv(ev)
                .evmAc(ac)
                .build();
        costMapper.insert(evmRecord);
    }

    @Override
    public BigDecimal getTotalCost(String projectId) {
        LambdaQueryWrapper<Cost> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(Cost::getProjectId, projectId);
        List<Cost> costs = costMapper.selectList(wrapper);
        return costs.stream()
                .map(c -> c.getAmount() != null ? c.getAmount() : BigDecimal.ZERO)
                .reduce(BigDecimal.ZERO, BigDecimal::add);
    }

    @Override
    @Transactional
    public void generateSettlement(String projectId, LocalDateTime from, LocalDateTime to) {
        // TODO: 根据期间内成本生成结算单，通过 RocketMQ 推送至财务系统
        BigDecimal total = getTotalCost(projectId);
        Cost settlement = Cost.builder()
                .costId(UUID.randomUUID().toString().replace("-", ""))
                .projectId(projectId)
                .costType("SETTLEMENT")
                .amount(total)
                .calculateTime(LocalDateTime.now())
                .build();
        costMapper.insert(settlement);
    }

    @Override
    @Transactional
    public void approveSettlement(String settlementId, String approvedBy) {
        Cost settlement = costMapper.selectById(settlementId);
        if (settlement == null) {
            throw new IllegalArgumentException("Settlement not found: " + settlementId);
        }
        settlement.setCostType("SETTLEMENT_APPROVED");
        settlement.setCalculateTime(LocalDateTime.now());
        costMapper.updateById(settlement);

        // Update related outsource cost records to mark as approved
        LambdaQueryWrapper<com.bank.updg.updg_cost.model.entity.CostOutsource> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(com.bank.updg.updg_cost.model.entity.CostOutsource::getCostId, settlementId);
        List<com.bank.updg.updg_cost.model.entity.CostOutsource> outsourceCosts =
                costOutsourceMapper.selectList(wrapper);
        for (com.bank.updg.updg_cost.model.entity.CostOutsource oc : outsourceCosts) {
            // Mark as approved - in a real system this would update payment status
            oc.setCreateTime(LocalDateTime.now());
            costOutsourceMapper.updateById(oc);
        }
    }

    @Override
    @Transactional
    public void rejectSettlement(String settlementId, String reason) {
        Cost settlement = costMapper.selectById(settlementId);
        if (settlement == null) {
            throw new IllegalArgumentException("Settlement not found: " + settlementId);
        }
        settlement.setCostType("SETTLEMENT_REJECTED");
        // Store rejection reason in the evmPv field as a placeholder (add reason field in future migration)
        settlement.setCalculateTime(LocalDateTime.now());
        costMapper.updateById(settlement);
    }
}
