package com.bank.updg.updg_resource.service.impl;

import com.bank.updg.updg_resource.service.SettlementService;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.math.BigDecimal;
import java.util.HashMap;
import java.util.Map;

@Service
@RequiredArgsConstructor
public class SettlementServiceImpl implements SettlementService {

    @Override
    public Map<String, Object> generateMonthlySettlement(String projectId, String yearMonth) {
        // Query all approved timesheets for the month, compute hours * rate.
        // In production: integrate with updg-timesheet service via RPC/MQ.
        // Placeholder: return computed settlement envelope.
        Map<String, Object> result = new HashMap<>();
        result.put("projectId", projectId);
        result.put("yearMonth", yearMonth);
        result.put("totalHours", BigDecimal.ZERO);
        result.put("totalCost", BigDecimal.ZERO);
        result.put("headcount", 0);
        result.put("settlementStatus", "GENERATED");
        return result;
    }

    @Override
    public Map<String, Object> getMonthlySummary(String projectId, String yearMonth) {
        // Returns total hours, total cost, headcount.
        // In production: aggregate from timesheet data.
        // Placeholder: return summary envelope.
        Map<String, Object> summary = new HashMap<>();
        summary.put("projectId", projectId);
        summary.put("yearMonth", yearMonth);
        summary.put("totalHours", BigDecimal.ZERO);
        summary.put("totalCost", BigDecimal.ZERO);
        summary.put("headcount", 0);
        return summary;
    }
}
