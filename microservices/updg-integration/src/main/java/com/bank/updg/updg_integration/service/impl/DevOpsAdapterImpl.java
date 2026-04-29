package com.bank.updg.updg_integration.service.impl;

import com.bank.updg.updg_integration.service.DevOpsAdapter;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

import java.util.Map;

/**
 * DevOps / 大禹 testing system integration.
 */
@Slf4j
@Service
public class DevOpsAdapterImpl implements DevOpsAdapter {

    @Value("${integration.devops.base-url:}")
    private String devopsBaseUrl;

    // TODO: integrate DevOps REST API

    @Override
    public Map<String, Object> getBuildStatus(String projectId) {
        log.info("Fetching build status for project: {}", projectId);
        return Map.of("projectId", projectId, "buildStatus", "DEVOPS_NOT_CONNECTED");
    }

    @Override
    public Map<String, Object> getTestResults(String projectId) {
        log.info("Fetching test results for project: {}", projectId);
        return Map.of("projectId", projectId, "testStatus", "DEVOPS_NOT_CONNECTED");
    }
}
