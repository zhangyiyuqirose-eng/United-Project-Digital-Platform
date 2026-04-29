package com.bank.updg.updg_cost.service;

import com.bank.updg.updg_cost.model.entity.Budget;

import java.math.BigDecimal;
import java.util.Map;

public interface BudgetService {

    Budget createBudget(Budget budgetData);

    void updateBudget(String budgetId, Budget data);

    Budget getBudget(String projectId);

    Map<String, Object> getBudgetExecution(String projectId);

    boolean checkBudget(String projectId, BigDecimal amount);
}
