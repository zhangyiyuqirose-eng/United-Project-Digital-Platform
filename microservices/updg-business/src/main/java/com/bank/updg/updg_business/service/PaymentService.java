package com.bank.updg.updg_business.service;

import com.baomidou.mybatisplus.extension.service.IService;
import com.bank.updg.updg_business.model.entity.ContractPayment;

import java.util.List;

public interface PaymentService extends IService<ContractPayment> {

    void createPaymentPlan(String contractId, List<ContractPayment> plans);

    void updatePayment(String paymentId, String actualDate, String status);

    List<ContractPayment> getPaymentsByContract(String contractId);

    List<ContractPayment> getOverduePayments();
}
