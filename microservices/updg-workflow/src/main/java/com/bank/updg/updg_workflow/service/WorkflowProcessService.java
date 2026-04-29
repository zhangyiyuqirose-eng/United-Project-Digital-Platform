package com.bank.updg.updg_workflow.service;

import java.util.List;
import java.util.Map;

/**
 * Workflow process management service
 * Handles BPMN deployment, process initiation, status tracking, and history queries.
 */
public interface WorkflowProcessService {

    /**
     * Auto-deploy all BPMN processes from classpath:processes/*.bpmn20.xml
     */
    void autoDeployOnStartup();

    /**
     * Manually deploy all BPMN processes from classpath
     */
    void deployAllProcesses();

    /**
     * Start project initiation approval process
     *
     * @param projectId project business ID
     * @param vars      process variables (pmoReviewer, deptLeader, budgetAmount, etc.)
     * @return process instance ID
     */
    String startInitiationProcess(String projectId, Map<String, Object> vars);

    /**
     * Start project change approval process
     *
     * @param changeId change request business ID
     * @param vars     process variables (projectManager, pmoApprover, isMajor, etc.)
     * @return process instance ID
     */
    String startChangeProcess(String changeId, Map<String, Object> vars);

    /**
     * Start project close approval process
     *
     * @param closeId close request business ID
     * @param vars    process variables (projectManager, qaReviewer, financeReviewer, etc.)
     * @return process instance ID
     */
    String startCloseProcess(String closeId, Map<String, Object> vars);

    /**
     * Get current process status by business key
     *
     * @param businessKey business ID
     * @return map containing current task, status, and process info
     */
    Map<String, Object> getProcessStatus(String businessKey);

    /**
     * Get full process history by business key
     *
     * @param businessKey business ID
     * @return list of historical process log entries
     */
    List<Map<String, Object>> getProcessHistory(String businessKey);
}
