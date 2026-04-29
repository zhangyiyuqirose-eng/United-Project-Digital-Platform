package com.bank.updg.updg_integration.service.impl;

import com.bank.updg.updg_integration.service.FinanceAdapter;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

import java.math.BigDecimal;

/**
 * Finance system integration via RocketMQ transaction messages.
 * Retry up to 3 times with 5-minute interval on failure.
 */
@Slf4j
@Service
public class FinanceAdapterImpl implements FinanceAdapter {

    // TODO: integrate RocketMQ transaction messages for finance settlement push

    @Override
    public void pushSettlement(String projectId, BigDecimal amount) {
        log.info("Pushing settlement to finance system: projectId={}, amount={}", projectId, amount);
        // TODO: send RocketMQ transaction message
    }

    @Override
    public String queryPaymentStatus(String settlementId) {
        log.info("Querying payment status: {}", settlementId);
        // TODO: REST call to finance system
        return "PENDING";
    }
}
