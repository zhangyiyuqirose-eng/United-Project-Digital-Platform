package com.bank.updg.updg_cost.controller;

import com.bank.updg.common.model.ApiResponse;
import com.bank.updg.updg_cost.model.entity.ExpenseReimbursement;
import com.bank.updg.updg_cost.service.ExpenseReimbursementService;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

import java.util.List;

/**
 * F-1104: Expense reimbursement management.
 */
@RestController
@RequestMapping("/api/cost/reimbursement")
@RequiredArgsConstructor
public class ExpenseReimbursementController {

    private final ExpenseReimbursementService reimbursementService;

    @PostMapping
    public ApiResponse<ExpenseReimbursement> create(@RequestBody ExpenseReimbursement reimbursement) {
        return ApiResponse.success(reimbursementService.createReimbursement(reimbursement));
    }

    @GetMapping("/staff/{staffId}")
    public ApiResponse<List<ExpenseReimbursement>> getByStaff(@PathVariable String staffId) {
        return ApiResponse.success(reimbursementService.getByStaffId(staffId));
    }

    @GetMapping("/project/{projectId}")
    public ApiResponse<List<ExpenseReimbursement>> getByProject(@PathVariable String projectId) {
        return ApiResponse.success(reimbursementService.getByProjectId(projectId));
    }

    @PostMapping("/{id}/submit")
    public ApiResponse<Void> submit(@PathVariable String id) {
        reimbursementService.submitReimbursement(id);
        return ApiResponse.success();
    }

    @PostMapping("/{id}/approve")
    public ApiResponse<Void> approve(@PathVariable String id) {
        reimbursementService.approveReimbursement(id);
        return ApiResponse.success();
    }

    @PostMapping("/{id}/reject")
    public ApiResponse<Void> reject(@PathVariable String id) {
        reimbursementService.rejectReimbursement(id);
        return ApiResponse.success();
    }

    @PostMapping("/{id}/paid")
    public ApiResponse<Void> markPaid(@PathVariable String id) {
        reimbursementService.markPaid(id);
        return ApiResponse.success();
    }
}
