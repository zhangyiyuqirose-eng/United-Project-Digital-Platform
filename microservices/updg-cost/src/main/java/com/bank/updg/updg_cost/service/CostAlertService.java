package com.bank.updg.updg_cost.service;

import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.bank.updg.updg_cost.model.entity.CostAlert;

import java.util.List;

public interface CostAlertService {

    List<CostAlert> checkCostAlerts(String projectId);

    CostAlert createAlert(CostAlert alertData);

    void acknowledgeAlert(String alertId, String userId);

    void resolveAlert(String alertId);

    Page<CostAlert> listAlerts(String projectId, String status, int page, int size);

    List<CostAlert> getActiveAlerts();
}
