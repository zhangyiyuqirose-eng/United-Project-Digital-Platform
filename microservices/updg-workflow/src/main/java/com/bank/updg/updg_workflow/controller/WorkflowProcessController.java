package com.bank.updg.updg_workflow.controller;

import com.bank.updg.common.model.ApiResponse;
import com.bank.updg.updg_workflow.service.WorkflowProcessService;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/workflow/process")
@RequiredArgsConstructor
public class WorkflowProcessController {

    private final WorkflowProcessService workflowProcessService;

    /**
     * Manually deploy all BPMN processes from classpath
     */
    @PostMapping("/deploy")
    public ApiResponse<String> deployAllProcesses() {
        workflowProcessService.deployAllProcesses();
        return ApiResponse.success("BPMN processes deployed");
    }

    /**
     * Start project initiation approval process
     */
    @PostMapping("/init/start")
    public ApiResponse<String> startInitiation(@RequestBody Map<String, Object> body) {
        String projectId = (String) body.get("projectId");
        @SuppressWarnings("unchecked")
        Map<String, Object> vars = (Map<String, Object>) body.get("variables");
        return ApiResponse.success(workflowProcessService.startInitiationProcess(projectId, vars));
    }

    /**
     * Start project change approval process
     */
    @PostMapping("/change/start")
    public ApiResponse<String> startChange(@RequestBody Map<String, Object> body) {
        String changeId = (String) body.get("changeId");
        @SuppressWarnings("unchecked")
        Map<String, Object> vars = (Map<String, Object>) body.get("variables");
        return ApiResponse.success(workflowProcessService.startChangeProcess(changeId, vars));
    }

    /**
     * Start project close approval process
     */
    @PostMapping("/close/start")
    public ApiResponse<String> startClose(@RequestBody Map<String, Object> body) {
        String closeId = (String) body.get("closeId");
        @SuppressWarnings("unchecked")
        Map<String, Object> vars = (Map<String, Object>) body.get("variables");
        return ApiResponse.success(workflowProcessService.startCloseProcess(closeId, vars));
    }

    /**
     * Get current process status by business key
     */
    @GetMapping("/status/{businessKey}")
    public ApiResponse<Map<String, Object>> getStatus(@PathVariable String businessKey) {
        return ApiResponse.success(workflowProcessService.getProcessStatus(businessKey));
    }

    /**
     * Get full process history by business key
     */
    @GetMapping("/history/{businessKey}")
    public ApiResponse<List<Map<String, Object>>> getHistory(@PathVariable String businessKey) {
        return ApiResponse.success(workflowProcessService.getProcessHistory(businessKey));
    }
}
