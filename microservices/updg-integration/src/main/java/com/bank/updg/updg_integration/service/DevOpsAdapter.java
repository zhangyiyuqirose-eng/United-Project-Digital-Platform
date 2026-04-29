package com.bank.updg.updg_integration.service;

import java.util.Map;

/**
 * DevOps / testing system adapter.
 */
public interface DevOpsAdapter {

    /**
     * Fetch build status from CI/CD system.
     */
    Map<String, Object> getBuildStatus(String projectId);

    /**
     * Fetch test results from 大禹 testing system.
     */
    Map<String, Object> getTestResults(String projectId);
}
