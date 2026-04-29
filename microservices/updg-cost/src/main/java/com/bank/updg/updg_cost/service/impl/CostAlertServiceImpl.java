package com.bank.updg.updg_cost.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.bank.updg.updg_cost.mapper.BudgetMapper;
import com.bank.updg.updg_cost.mapper.CostAlertMapper;
import com.bank.updg.updg_cost.mapper.CostMapper;
import com.bank.updg.updg_cost.model.entity.Budget;
import com.bank.updg.updg_cost.model.entity.Cost;
import com.bank.updg.updg_cost.model.entity.CostAlert;
import com.bank.updg.updg_cost.service.CostAlertService;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.*;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
public class CostAlertServiceImpl implements CostAlertService {

    private static final BigDecimal CPI_THRESHOLD = new BigDecimal("0.9");
    private static final BigDecimal SPI_THRESHOLD = new BigDecimal("0.9");

    private final CostAlertMapper costAlertMapper;
    private final BudgetMapper budgetMapper;
    private final CostMapper costMapper;

    @Override
    public List<CostAlert> checkCostAlerts(String projectId) {
        List<CostAlert> newAlerts = new ArrayList<>();

        // Check 1: Budget overrun
        Budget budget = budgetMapper.selectOne(
                new LambdaQueryWrapper<Budget>()
                        .eq(Budget::getProjectId, projectId)
                        .orderByDesc(Budget::getCreateTime)
                        .last("LIMIT 1"));

        if (budget != null && budget.getTotalBudget() != null) {
            List<Cost> costs = costMapper.selectList(
                    new LambdaQueryWrapper<Cost>()
                            .eq(Cost::getProjectId, projectId));

            BigDecimal actualTotal = costs.stream()
                    .map(Cost::getAmount)
                    .filter(a -> a != null)
                    .reduce(BigDecimal.ZERO, BigDecimal::add);

            if (actualTotal.compareTo(budget.getTotalBudget()) > 0) {
                CostAlert alert = CostAlert.builder()
                        .alertId(UUID.randomUUID().toString().replace("-", ""))
                        .projectId(projectId)
                        .alertType("BUDGET_OVER_RUN")
                        .severity("CRITICAL")
                        .message("Budget exceeded: actual " + actualTotal + " vs budget " + budget.getTotalBudget())
                        .currentValue(actualTotal)
                        .threshold(budget.getTotalBudget())
                        .status("ACTIVE")
                        .createdBy("SYSTEM")
                        .createTime(LocalDateTime.now())
                        .build();
                costAlertMapper.insert(alert);
                newAlerts.add(alert);
            }
        }

        // Check 2 & 3: CPI and SPI from cost EVM data
        List<Cost> costs = costMapper.selectList(
                new LambdaQueryWrapper<Cost>()
                        .eq(Cost::getProjectId, projectId));

        BigDecimal totalPv = costs.stream().map(Cost::getEvmPv).filter(v -> v != null).reduce(BigDecimal.ZERO, BigDecimal::add);
        BigDecimal totalEv = costs.stream().map(Cost::getEvmEv).filter(v -> v != null).reduce(BigDecimal.ZERO, BigDecimal::add);
        BigDecimal totalAc = costs.stream().map(Cost::getEvmAc).filter(v -> v != null).reduce(BigDecimal.ZERO, BigDecimal::add);

        if (totalEv.compareTo(BigDecimal.ZERO) > 0 && totalAc.compareTo(BigDecimal.ZERO) > 0) {
            BigDecimal cpi = totalEv.divide(totalAc, 4, BigDecimal.ROUND_HALF_UP);
            if (cpi.compareTo(CPI_THRESHOLD) < 0) {
                CostAlert alert = CostAlert.builder()
                        .alertId(UUID.randomUUID().toString().replace("-", ""))
                        .projectId(projectId)
                        .alertType("CPI_LOW")
                        .severity("WARNING")
                        .message("CPI is below threshold: " + cpi + " < " + CPI_THRESHOLD)
                        .currentValue(cpi)
                        .threshold(CPI_THRESHOLD)
                        .status("ACTIVE")
                        .createdBy("SYSTEM")
                        .createTime(LocalDateTime.now())
                        .build();
                costAlertMapper.insert(alert);
                newAlerts.add(alert);
            }
        }

        if (totalPv.compareTo(BigDecimal.ZERO) > 0 && totalEv.compareTo(BigDecimal.ZERO) > 0) {
            BigDecimal spi = totalEv.divide(totalPv, 4, BigDecimal.ROUND_HALF_UP);
            if (spi.compareTo(SPI_THRESHOLD) < 0) {
                CostAlert alert = CostAlert.builder()
                        .alertId(UUID.randomUUID().toString().replace("-", ""))
                        .projectId(projectId)
                        .alertType("SPI_LOW")
                        .severity("WARNING")
                        .message("SPI is below threshold: " + spi + " < " + SPI_THRESHOLD)
                        .currentValue(spi)
                        .threshold(SPI_THRESHOLD)
                        .status("ACTIVE")
                        .createdBy("SYSTEM")
                        .createTime(LocalDateTime.now())
                        .build();
                costAlertMapper.insert(alert);
                newAlerts.add(alert);
            }
        }

        return newAlerts;
    }

    @Override
    public CostAlert createAlert(CostAlert alertData) {
        alertData.setAlertId(UUID.randomUUID().toString().replace("-", ""));
        alertData.setStatus("ACTIVE");
        alertData.setCreateTime(LocalDateTime.now());
        costAlertMapper.insert(alertData);
        return alertData;
    }

    @Override
    public void acknowledgeAlert(String alertId, String userId) {
        CostAlert alert = costAlertMapper.selectById(alertId);
        if (alert == null) {
            throw new IllegalArgumentException("Alert not found: " + alertId);
        }
        alert.setStatus("ACKNOWLEDGED");
        alert.setAckTime(LocalDateTime.now());
        costAlertMapper.updateById(alert);
    }

    @Override
    public void resolveAlert(String alertId) {
        CostAlert alert = costAlertMapper.selectById(alertId);
        if (alert == null) {
            throw new IllegalArgumentException("Alert not found: " + alertId);
        }
        alert.setStatus("RESOLVED");
        alert.setResolveTime(LocalDateTime.now());
        costAlertMapper.updateById(alert);
    }

    @Override
    public Page<CostAlert> listAlerts(String projectId, String status, int page, int size) {
        Page<CostAlert> pageObj = new Page<>(page, size);
        LambdaQueryWrapper<CostAlert> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(CostAlert::getProjectId, projectId);
        if (status != null && !status.isEmpty()) {
            wrapper.eq(CostAlert::getStatus, status);
        }
        wrapper.orderByDesc(CostAlert::getCreateTime);
        return costAlertMapper.selectPage(pageObj, wrapper);
    }

    @Override
    public List<CostAlert> getActiveAlerts() {
        return costAlertMapper.selectList(
                new LambdaQueryWrapper<CostAlert>()
                        .eq(CostAlert::getStatus, "ACTIVE")
                        .orderByDesc(CostAlert::getCreateTime));
    }
}
