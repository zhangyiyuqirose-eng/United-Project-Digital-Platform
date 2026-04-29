package com.bank.updg.updg_cost.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import com.bank.updg.updg_cost.mapper.ExpenseReimbursementMapper;
import com.bank.updg.updg_cost.model.entity.ExpenseReimbursement;
import com.bank.updg.updg_cost.service.ExpenseReimbursementService;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
import java.util.List;
import java.util.UUID;

@Service
public class ExpenseReimbursementServiceImpl
        extends ServiceImpl<ExpenseReimbursementMapper, ExpenseReimbursement>
        implements ExpenseReimbursementService {

    @Override
    public ExpenseReimbursement createReimbursement(ExpenseReimbursement reimbursement) {
        reimbursement.setId(UUID.randomUUID().toString().replace("-", ""));
        reimbursement.setStatus("DRAFT");
        save(reimbursement);
        return reimbursement;
    }

    @Override
    public List<ExpenseReimbursement> getByStaffId(String staffId) {
        LambdaQueryWrapper<ExpenseReimbursement> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(ExpenseReimbursement::getStaffId, staffId);
        return list(wrapper);
    }

    @Override
    public List<ExpenseReimbursement> getByProjectId(String projectId) {
        LambdaQueryWrapper<ExpenseReimbursement> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(ExpenseReimbursement::getProjectId, projectId);
        return list(wrapper);
    }

    @Override
    public void submitReimbursement(String id) {
        ExpenseReimbursement r = getById(id);
        if (r != null) {
            r.setStatus("SUBMITTED");
            r.setSubmittedAt(LocalDateTime.now());
            updateById(r);
        }
    }

    @Override
    public void approveReimbursement(String id) {
        ExpenseReimbursement r = getById(id);
        if (r != null) {
            r.setStatus("APPROVED");
            r.setApprovedAt(LocalDateTime.now());
            updateById(r);
        }
    }

    @Override
    public void rejectReimbursement(String id) {
        ExpenseReimbursement r = getById(id);
        if (r != null) {
            r.setStatus("REJECTED");
            updateById(r);
        }
    }

    @Override
    public void markPaid(String id) {
        ExpenseReimbursement r = getById(id);
        if (r != null) {
            r.setStatus("PAID");
            r.setPaidAt(LocalDateTime.now());
            updateById(r);
        }
    }
}
