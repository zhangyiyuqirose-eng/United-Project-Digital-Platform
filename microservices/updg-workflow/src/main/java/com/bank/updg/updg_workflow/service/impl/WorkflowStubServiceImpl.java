package com.bank.updg.updg_workflow.service.impl;

import com.bank.updg.updg_workflow.service.WorkflowService;
import lombok.extern.slf4j.Slf4j;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.stereotype.Service;

import java.util.*;

/**
 * WorkflowStubServiceImpl - Stub implementation when Flowable is disabled.
 * Returns placeholder responses indicating workflow functionality is unavailable.
 */
@Slf4j
@Service
@ConditionalOnProperty(name = "flowable.enabled", havingValue = "false", matchIfMissing = true)
public class WorkflowStubServiceImpl implements WorkflowService {

    @Override
    public String startProcess(String processDefinitionKey, String businessKey,
                               String initiator, Map<String, Object> variables) {
        log.warn("Workflow functionality is disabled. Cannot start process: key={}", processDefinitionKey);
        throw new UnsupportedOperationException("Workflow functionality is disabled. Enable flowable.enabled=true to use workflow features.");
    }

    @Override
    public void approveTask(String taskId, String comment, boolean approved) {
        log.warn("Workflow functionality is disabled. Cannot approve task: taskId={}", taskId);
        throw new UnsupportedOperationException("Workflow functionality is disabled. Enable flowable.enabled=true to use workflow features.");
    }

    @Override
    public List<Map<String, Object>> getPendingTasks(String assignee) {
        log.warn("Workflow functionality is disabled. Cannot get pending tasks for: {}", assignee);
        return Collections.emptyList();
    }

    @Override
    public List<Map<String, Object>> getProcessLog(String businessId) {
        log.warn("Workflow functionality is disabled. Cannot get process log for: {}", businessId);
        return Collections.emptyList();
    }
}