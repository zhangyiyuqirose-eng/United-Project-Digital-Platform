package com.bank.updg.updg_workflow.service.impl;

import com.bank.updg.updg_workflow.service.WorkflowProcessService;
import lombok.extern.slf4j.Slf4j;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.stereotype.Service;

import java.util.*;

/**
 * WorkflowProcessStubServiceImpl - Stub implementation when Flowable is disabled.
 * Returns placeholder responses indicating workflow functionality is unavailable.
 */
@Slf4j
@Service
@ConditionalOnProperty(name = "flowable.enabled", havingValue = "false", matchIfMissing = true)
public class WorkflowProcessStubServiceImpl implements WorkflowProcessService {

    @Override
    public void autoDeployOnStartup() {
        log.info("Workflow functionality is disabled. Skipping BPMN deployment.");
    }

    @Override
    public void deployAllProcesses() {
        log.warn("Workflow functionality is disabled. Cannot deploy processes.");
    }

    @Override
    public String startInitiationProcess(String projectId, Map<String, Object> vars) {
        log.warn("Workflow functionality is disabled. Cannot start initiation process: projectId={}", projectId);
        throw new UnsupportedOperationException("Workflow functionality is disabled. Enable flowable.enabled=true to use workflow features.");
    }

    @Override
    public String startChangeProcess(String changeId, Map<String, Object> vars) {
        log.warn("Workflow functionality is disabled. Cannot start change process: changeId={}", changeId);
        throw new UnsupportedOperationException("Workflow functionality is disabled. Enable flowable.enabled=true to use workflow features.");
    }

    @Override
    public String startCloseProcess(String closeId, Map<String, Object> vars) {
        log.warn("Workflow functionality is disabled. Cannot start close process: closeId={}", closeId);
        throw new UnsupportedOperationException("Workflow functionality is disabled. Enable flowable.enabled=true to use workflow features.");
    }

    @Override
    public Map<String, Object> getProcessStatus(String businessKey) {
        Map<String, Object> result = new LinkedHashMap<>();
        result.put("businessKey", businessKey);
        result.put("status", "DISABLED");
        result.put("message", "Workflow functionality is disabled");
        result.put("currentTasks", Collections.emptyList());
        return result;
    }

    @Override
    public List<Map<String, Object>> getProcessHistory(String businessKey) {
        log.warn("Workflow functionality is disabled. Cannot get process history for: {}", businessKey);
        return Collections.emptyList();
    }
}