package com.bank.updg.updg_business.service;

import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.baomidou.mybatisplus.extension.service.IService;
import com.bank.updg.updg_business.model.entity.ProcurementPlan;

import java.util.List;

public interface ProcurementPlanService extends IService<ProcurementPlan> {

    ProcurementPlan createPlan(ProcurementPlan data);

    void updatePlan(String planId, ProcurementPlan data);

    ProcurementPlan getPlan(String planId);

    Page<ProcurementPlan> listPlans(String projectId, String status, int page, int size);

    List<ProcurementPlan> getByProjectId(String projectId);

    List<ProcurementPlan> getOverdue();
}
