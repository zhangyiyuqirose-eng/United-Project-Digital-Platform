package com.bank.updg.updg_integration.service.impl;

import com.bank.updg.updg_integration.service.HrAdapter;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

import java.util.Map;

/**
 * HR system integration via REST API.
 * Retry up to 3 times with 5-minute interval on failure.
 */
@Slf4j
@Service
public class HrAdapterImpl implements HrAdapter {

    @Value("${integration.hr.base-url:}")
    private String hrBaseUrl;

    // TODO: integrate actual HR system REST API with retry logic

    @Override
    public Map<String, Object> getEmployeeInfo(String employeeId) {
        log.info("Fetching employee info from HR system: {}", employeeId);
        // TODO: REST call to HR system with retry
        return Map.of("employeeId", employeeId, "status", "HR_NOT_CONNECTED");
    }

    @Override
    public void syncOrgStructure() {
        log.info("Syncing org structure from HR system");
        // TODO: periodic sync job
    }
}
