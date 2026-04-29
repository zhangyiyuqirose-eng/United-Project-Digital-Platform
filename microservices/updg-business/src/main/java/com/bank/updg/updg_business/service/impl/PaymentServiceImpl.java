package com.bank.updg.updg_business.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import com.bank.updg.updg_business.mapper.ContractPaymentMapper;
import com.bank.updg.updg_business.model.entity.ContractPayment;
import com.bank.updg.updg_business.service.PaymentService;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.UUID;

@Service
@RequiredArgsConstructor
public class PaymentServiceImpl extends ServiceImpl<ContractPaymentMapper, ContractPayment>
        implements PaymentService {

    @Override
    public void createPaymentPlan(String contractId, List<ContractPayment> plans) {
        for (ContractPayment plan : plans) {
            plan.setContractId(contractId);
            if (plan.getPaymentId() == null || plan.getPaymentId().isEmpty()) {
                plan.setPaymentId(UUID.randomUUID().toString());
            }
            if (plan.getStatus() == null) {
                plan.setStatus("PENDING");
            }
            save(plan);
        }
    }

    @Override
    public void updatePayment(String paymentId, String actualDate, String status) {
        ContractPayment payment = getById(paymentId);
        if (payment == null) {
            throw new RuntimeException("Payment not found: " + paymentId);
        }
        if (actualDate != null) {
            payment.setActualDate(actualDate);
        }
        if (status != null) {
            payment.setStatus(status);
        }
        updateById(payment);
    }

    @Override
    public List<ContractPayment> getPaymentsByContract(String contractId) {
        return list(new LambdaQueryWrapper<ContractPayment>()
                .eq(ContractPayment::getContractId, contractId)
                .orderByAsc(ContractPayment::getDueDate));
    }

    @Override
    public List<ContractPayment> getOverduePayments() {
        // Fetch pending/partial payments and check due date
        List<ContractPayment> payments = list(new LambdaQueryWrapper<ContractPayment>()
                .in(ContractPayment::getStatus, "PENDING", "PARTIAL")
                .isNotNull(ContractPayment::getDueDate));

        java.time.LocalDate now = java.time.LocalDate.now();
        return payments.stream()
                .filter(p -> {
                    try {
                        java.time.LocalDate due = java.time.LocalDate.parse(p.getDueDate());
                        return due.isBefore(now);
                    } catch (Exception e) {
                        return false;
                    }
                })
                .toList();
    }
}
