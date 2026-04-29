package com.bank.updg.updg_integration.service;

import java.util.Map;

/**
 * HR system adapter (anti-corruption layer).
 */
public interface HrAdapter {

    /**
     * Fetch employee info from HR system.
     */
    Map<String, Object> getEmployeeInfo(String employeeId);

    /**
     * Sync org structure from HR system.
     */
    void syncOrgStructure();
}
