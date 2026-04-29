package com.bank.updg.updg_workflow.service;

import java.util.List;
import java.util.Map;

public interface WorkflowService {

    String startProcess(String processDefinitionKey, String businessKey,
                        String initiator, Map<String, Object> variables);

    void approveTask(String taskId, String comment, boolean approved);

    List<Map<String, Object>> getPendingTasks(String assignee);

    List<Map<String, Object>> getProcessLog(String businessId);
}
