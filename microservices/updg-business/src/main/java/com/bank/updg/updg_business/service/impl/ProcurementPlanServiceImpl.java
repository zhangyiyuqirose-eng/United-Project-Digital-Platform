package com.bank.updg.updg_business.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import com.bank.updg.updg_business.mapper.ProcurementPlanMapper;
import com.bank.updg.updg_business.model.entity.ProcurementPlan;
import com.bank.updg.updg_business.service.ProcurementPlanService;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.time.LocalDate;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.List;
import java.util.UUID;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
public class ProcurementPlanServiceImpl extends ServiceImpl<ProcurementPlanMapper, ProcurementPlan>
        implements ProcurementPlanService {

    @Override
    public ProcurementPlan createPlan(ProcurementPlan data) {
        if (data.getPlanId() == null || data.getPlanId().isEmpty()) {
            data.setPlanId(UUID.randomUUID().toString());
        }
        if (data.getStatus() == null) {
            data.setStatus("PLANNED");
        }
        String now = LocalDateTime.now().format(DateTimeFormatter.ISO_LOCAL_DATE_TIME);
        data.setCreatedAt(now);
        data.setUpdatedAt(now);
        save(data);
        return data;
    }

    @Override
    public void updatePlan(String planId, ProcurementPlan data) {
        ProcurementPlan existing = getById(planId);
        if (existing == null) {
            throw new RuntimeException("Procurement plan not found: " + planId);
        }
        if (data.getName() != null) existing.setName(data.getName());
        if (data.getCategory() != null) existing.setCategory(data.getCategory());
        if (data.getEstimatedCost() != null) existing.setEstimatedCost(data.getEstimatedCost());
        if (data.getSupplierId() != null) existing.setSupplierId(data.getSupplierId());
        if (data.getRequiredDate() != null) existing.setRequiredDate(data.getRequiredDate());
        if (data.getStatus() != null) existing.setStatus(data.getStatus());
        if (data.getPriority() != null) existing.setPriority(data.getPriority());
        if (data.getDescription() != null) existing.setDescription(data.getDescription());
        existing.setUpdatedAt(LocalDateTime.now().format(DateTimeFormatter.ISO_LOCAL_DATE_TIME));
        updateById(existing);
    }

    @Override
    public ProcurementPlan getPlan(String planId) {
        return getById(planId);
    }

    @Override
    public Page<ProcurementPlan> listPlans(String projectId, String status, int page, int size) {
        Page<ProcurementPlan> pageObj = new Page<>(page, size);
        LambdaQueryWrapper<ProcurementPlan> wrapper = new LambdaQueryWrapper<ProcurementPlan>()
                .orderByDesc(ProcurementPlan::getCreatedAt);
        if (projectId != null) {
            wrapper.eq(ProcurementPlan::getProjectId, projectId);
        }
        if (status != null) {
            wrapper.eq(ProcurementPlan::getStatus, status);
        }
        return page(pageObj, wrapper);
    }

    @Override
    public List<ProcurementPlan> getByProjectId(String projectId) {
        return list(new LambdaQueryWrapper<ProcurementPlan>()
                .eq(ProcurementPlan::getProjectId, projectId)
                .orderByDesc(ProcurementPlan::getCreatedAt));
    }

    @Override
    public List<ProcurementPlan> getOverdue() {
        List<ProcurementPlan> all = list(new LambdaQueryWrapper<ProcurementPlan>()
                .in(ProcurementPlan::getStatus, "PLANNED", "IN_PROGRESS")
                .isNotNull(ProcurementPlan::getRequiredDate));
        String today = LocalDate.now().format(DateTimeFormatter.ISO_LOCAL_DATE);
        return all.stream()
                .filter(p -> p.getRequiredDate().compareTo(today) < 0)
                .collect(Collectors.toList());
    }
}
