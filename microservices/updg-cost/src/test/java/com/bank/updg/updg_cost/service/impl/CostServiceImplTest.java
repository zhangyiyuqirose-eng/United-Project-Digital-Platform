package com.bank.updg.updg_cost.service.impl;

import com.bank.updg.updg_cost.mapper.BudgetMapper;
import com.bank.updg.updg_cost.mapper.CostMapper;
import com.bank.updg.updg_cost.mapper.CostOutsourceMapper;
import com.bank.updg.updg_cost.model.entity.Budget;
import com.bank.updg.updg_cost.model.entity.Cost;
import com.bank.updg.updg_cost.service.CostCalculationService;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.ArgumentCaptor;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import java.math.BigDecimal;
import java.util.List;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
class CostServiceImplTest {

    @Mock
    private CostMapper costMapper;

    @Mock
    private CostOutsourceMapper costOutsourceMapper;

    @Mock
    private BudgetMapper budgetMapper;

    @Mock
    private CostCalculationService costCalculationService;

    private CostServiceImpl service;

    @BeforeEach
    void setUp() {
        service = new CostServiceImpl(costMapper, costOutsourceMapper, budgetMapper, costCalculationService);
    }

    @Test
    @DisplayName("getTotalCost - sums all costs for project")
    void getTotalCost_sumsAllCosts() {
        when(costMapper.selectList(any())).thenReturn(List.of(
                costWithAmount(new BigDecimal("5000")),
                costWithAmount(new BigDecimal("3000")),
                costWithAmount(new BigDecimal("2000"))
        ));

        BigDecimal total = service.getTotalCost("proj1");

        assertThat(total).isEqualByComparingTo(new BigDecimal("10000"));
    }

    @Test
    @DisplayName("getTotalCost - no costs returns zero")
    void getTotalCost_noCosts_returnsZero() {
        when(costMapper.selectList(any())).thenReturn(List.of());

        BigDecimal total = service.getTotalCost("proj1");

        assertThat(total).isEqualByComparingTo(BigDecimal.ZERO);
    }

    @Test
    @DisplayName("getTotalCost - null amounts treated as zero")
    void getTotalCost_nullAmounts_treatedAsZero() {
        when(costMapper.selectList(any())).thenReturn(List.of(
                costWithAmount(new BigDecimal("1000")),
                costWithAmount(null),
                costWithAmount(new BigDecimal("500"))
        ));

        BigDecimal total = service.getTotalCost("proj1");

        assertThat(total).isEqualByComparingTo(new BigDecimal("1500"));
    }

    @Test
    @DisplayName("calculateEvm - creates EVM snapshot with correct values")
    void calculateEvm_createsSnapshotWithCorrectValues() {
        Budget budget = new Budget();
        budget.setProjectId("proj1");
        budget.setTotalBudget(new BigDecimal("100000"));
        when(budgetMapper.selectOne(any())).thenReturn(budget);
        when(costMapper.selectList(any())).thenReturn(List.of(
                costWithAmount(new BigDecimal("40000"))
        ));
        when(costCalculationService.calculateLaborCost(eq("proj1"), any(), any()))
                .thenReturn(new BigDecimal("1000"));
        when(costCalculationService.calculateCompletedLaborCost("proj1"))
                .thenReturn(new BigDecimal("600"));

        service.calculateEvm("proj1");

        ArgumentCaptor<Cost> captor = ArgumentCaptor.forClass(Cost.class);
        verify(costMapper).insert(captor.capture());

        Cost snapshot = captor.getValue();
        assertThat(snapshot.getCostType()).isEqualTo("EVM_SNAPSHOT");
        assertThat(snapshot.getEvmPv()).isEqualByComparingTo(new BigDecimal("100000"));
        assertThat(snapshot.getEvmAc()).isEqualByComparingTo(new BigDecimal("40000"));
        // EV = 100000 * 600 / 1000 = 60000
        assertThat(snapshot.getEvmEv()).isEqualByComparingTo(new BigDecimal("60000"));
    }

    @Test
    @DisplayName("calculateEvm - no budget skips calculation")
    void calculateEvm_noBudget_skips() {
        when(budgetMapper.selectOne(any())).thenReturn(null);

        service.calculateEvm("proj1");

        verify(costMapper, never()).insert(any(Cost.class));
    }

    @Test
    @DisplayName("approveSettlement - throws when settlement not found")
    void approveSettlement_notFound_throws() {
        when(costMapper.selectById("nonexistent")).thenReturn(null);

        assertThatThrownBy(() -> service.approveSettlement("nonexistent", "admin"))
                .isInstanceOf(IllegalArgumentException.class)
                .hasMessageContaining("Settlement not found");
    }

    @Test
    @DisplayName("rejectSettlement - throws when settlement not found")
    void rejectSettlement_notFound_throws() {
        when(costMapper.selectById("nonexistent")).thenReturn(null);

        assertThatThrownBy(() -> service.rejectSettlement("nonexistent", "invalid data"))
                .isInstanceOf(IllegalArgumentException.class)
                .hasMessageContaining("Settlement not found");
    }

    private Cost costWithAmount(BigDecimal amount) {
        return Cost.builder()
                .costId(java.util.UUID.randomUUID().toString().replace("-", ""))
                .projectId("proj1")
                .costType("LABOR")
                .amount(amount)
                .calculateTime(java.time.LocalDateTime.now())
                .build();
    }
}
