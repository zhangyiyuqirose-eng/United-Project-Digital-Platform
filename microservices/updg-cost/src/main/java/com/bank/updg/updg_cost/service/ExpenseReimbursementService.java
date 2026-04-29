package com.bank.updg.updg_cost.service;

import com.baomidou.mybatisplus.extension.service.IService;
import com.bank.updg.updg_cost.model.entity.ExpenseReimbursement;

import java.util.List;

public interface ExpenseReimbursementService extends IService<ExpenseReimbursement> {

    ExpenseReimbursement createReimbursement(ExpenseReimbursement reimbursement);

    List<ExpenseReimbursement> getByStaffId(String staffId);

    List<ExpenseReimbursement> getByProjectId(String projectId);

    void submitReimbursement(String id);

    void approveReimbursement(String id);

    void rejectReimbursement(String id);

    void markPaid(String id);
}
