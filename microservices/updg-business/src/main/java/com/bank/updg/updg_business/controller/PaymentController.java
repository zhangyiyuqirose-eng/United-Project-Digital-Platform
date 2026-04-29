package com.bank.updg.updg_business.controller;

import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.bank.updg.common.model.ApiResponse;
import com.bank.updg.updg_business.model.entity.ContractPayment;
import com.bank.updg.updg_business.service.PaymentService;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/business/payment")
@RequiredArgsConstructor
public class PaymentController {

    private final PaymentService paymentService;

    @GetMapping("/list")
    public ApiResponse<Page<ContractPayment>> listPage(
            @RequestParam(defaultValue = "1") int page,
            @RequestParam(defaultValue = "10") int limit,
            @RequestParam(required = false) String contractId,
            @RequestParam(required = false) String status) {
        Page<ContractPayment> pageObj = new Page<>(page, limit);
        return ApiResponse.success(paymentService.page(pageObj));
    }

    @PostMapping("/create")
    public ApiResponse<Void> createPayment(@RequestBody ContractPayment payment) {
        paymentService.save(payment);
        return ApiResponse.success();
    }

    @PostMapping("/plan")
    public ApiResponse<Void> createPaymentPlan(
            @RequestParam String contractId,
            @RequestBody List<ContractPayment> plans) {
        paymentService.createPaymentPlan(contractId, plans);
        return ApiResponse.success();
    }

    @PutMapping("/{id}")
    public ApiResponse<Void> updatePayment(
            @PathVariable String id,
            @RequestParam(required = false) String actualDate,
            @RequestParam(required = false) String status) {
        paymentService.updatePayment(id, actualDate, status);
        return ApiResponse.success();
    }

    @GetMapping("/contract/{contractId}")
    public ApiResponse<List<ContractPayment>> getPaymentsByContract(@PathVariable String contractId) {
        return ApiResponse.success(paymentService.getPaymentsByContract(contractId));
    }

    @GetMapping("/overdue")
    public ApiResponse<List<ContractPayment>> getOverduePayments() {
        return ApiResponse.success(paymentService.getOverduePayments());
    }
}
