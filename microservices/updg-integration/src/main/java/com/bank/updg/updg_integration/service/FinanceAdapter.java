package com.bank.updg.updg_integration.service;

import java.math.BigDecimal;

/**
 * Finance system adapter via RocketMQ transaction messages.
 */
public interface FinanceAdapter {

    /**
     * Push settlement data to finance system via MQ.
     */
    void pushSettlement(String projectId, BigDecimal amount);

    /**
     * Query payment status from finance system.
     */
    String queryPaymentStatus(String settlementId);
}
