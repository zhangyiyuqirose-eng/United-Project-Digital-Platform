package com.bank.updg.updg_cost.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.bank.updg.updg_cost.mapper.CostMapper;
import com.bank.updg.updg_cost.mapper.CostOutsourceMapper;
import com.bank.updg.updg_cost.model.entity.Cost;
import com.bank.updg.updg_cost.model.entity.CostOutsource;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.List;
import java.util.Map;

import static org.assertj.core.api.Assertions.assertThat;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
class CostCalculationServiceImplTest {

    @Mock
    private CostMapper costMapper;

    @Mock
    private CostOutsourceMapper costOutsourceMapper;

    private CostCalculationServiceImpl service;

    @BeforeEach
    void setUp() {
        service = new CostCalculationServiceImpl(costMapper, costOutsourceMapper);
    }

    @Test
    @DisplayName("calculateLaborCost - sums existing LABOR costs")
    void calculateLaborCost_existingCosts_sumsCorrectly() {
        LocalDateTime from = LocalDateTime.now().minusDays(30);
        LocalDateTime to = LocalDateTime.now();

        when(costMapper.selectList(any(LambdaQueryWrapper.class)))
                .thenReturn(List.of(
                        laborCost("proj1", new BigDecimal("5000")),
                        laborCost("proj1", new BigDecimal("3000"))
                ));

        BigDecimal result = service.calculateLaborCost("proj1", from, to);

        assertThat(result).isEqualByComparingTo(new BigDecimal("8000"));
    }

    @Test
    @DisplayName("calculateLaborCost - no existing costs returns zero")
    void calculateLaborCost_noExistingCosts_returnsZero() {
        LocalDateTime from = LocalDateTime.now().minusDays(30);
        LocalDateTime to = LocalDateTime.now();

        when(costMapper.selectList(any(LambdaQueryWrapper.class))).thenReturn(List.of());

        BigDecimal result = service.calculateLaborCost("proj1", from, to);

        assertThat(result).isEqualByComparingTo(BigDecimal.ZERO);
    }

    @Test
    @DisplayName("getLaborCostBreakdown - groups costs by staff")
    void getLaborCostBreakdown_groupsByStaff() {
        Cost cost1 = costWithId("c1", "proj1");
        Cost cost2 = costWithId("c2", "proj1");
        when(costMapper.selectList(any())).thenReturn(List.of(cost1, cost2));

        when(costOutsourceMapper.selectList(any())).thenReturn(List.of(
                outsourceCost("c1", "staff-A", new BigDecimal("1000")),
                outsourceCost("c1", "staff-B", new BigDecimal("500")),
                outsourceCost("c2", "staff-A", new BigDecimal("2000"))
        ));

        List<Map<String, Object>> breakdown = service.getLaborCostBreakdown("proj1", null, null);

        assertThat(breakdown).hasSize(2);
        Map<String, Object> staffA = breakdown.stream()
                .filter(m -> m.get("staffId").equals("staff-A"))
                .findFirst()
                .orElseThrow();
        assertThat(staffA.get("totalCost")).isEqualTo(new BigDecimal("3000"));
    }

    @Test
    @DisplayName("getLaborCostBreakdown - empty project returns empty")
    void getLaborCostBreakdown_emptyProject_returnsEmpty() {
        when(costMapper.selectList(any())).thenReturn(List.of());
        when(costOutsourceMapper.selectList(any())).thenReturn(List.of());

        List<Map<String, Object>> breakdown = service.getLaborCostBreakdown("proj1", null, null);

        assertThat(breakdown).isEmpty();
    }

    @Test
    @DisplayName("calculateCompletedLaborCost - sums approved LABOR costs")
    void calculateCompletedLaborCost_sumsLaborCosts() {
        when(costMapper.selectList(any())).thenReturn(List.of(
                laborCost("proj1", new BigDecimal("4000")),
                laborCost("proj1", new BigDecimal("6000"))
        ));

        BigDecimal result = service.calculateCompletedLaborCost("proj1");

        assertThat(result).isEqualByComparingTo(new BigDecimal("10000"));
    }

    @Test
    @DisplayName("calculateCompletedLaborCost - no costs returns zero")
    void calculateCompletedLaborCost_noCosts_returnsZero() {
        when(costMapper.selectList(any())).thenReturn(List.of());

        BigDecimal result = service.calculateCompletedLaborCost("proj1");

        assertThat(result).isEqualByComparingTo(BigDecimal.ZERO);
    }

    private Cost laborCost(String projectId, BigDecimal amount) {
        return Cost.builder()
                .costId(java.util.UUID.randomUUID().toString().replace("-", ""))
                .projectId(projectId)
                .costType("LABOR")
                .amount(amount)
                .calculateTime(LocalDateTime.now())
                .build();
    }

    private Cost costWithId(String id, String projectId) {
        return Cost.builder()
                .costId(id)
                .projectId(projectId)
                .costType("LABOR")
                .amount(BigDecimal.ZERO)
                .calculateTime(LocalDateTime.now())
                .build();
    }

    private CostOutsource outsourceCost(String costId, String staffId, BigDecimal amount) {
        return CostOutsource.builder()
                .outsourceCostId(java.util.UUID.randomUUID().toString().replace("-", ""))
                .costId(costId)
                .staffId(staffId)
                .amount(amount)
                .createTime(LocalDateTime.now())
                .build();
    }
}
