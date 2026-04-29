package com.bank.updg.updg_workflow.controller;

import com.bank.updg.common.model.ApiResponse;
import com.bank.updg.updg_workflow.service.WorkflowService;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/workflow")
@RequiredArgsConstructor
public class WorkflowController {

    private final WorkflowService workflowService;

    @PostMapping("/start")
    public ApiResponse<String> start(@RequestBody Map<String, Object> body) {
        String processKey = (String) body.get("processDefinitionKey");
        String businessKey = (String) body.get("businessKey");
        String initiator = (String) body.get("initiator");
        @SuppressWarnings("unchecked")
        Map<String, Object> variables = (Map<String, Object>) body.get("variables");
        return ApiResponse.success(workflowService.startProcess(processKey, businessKey, initiator, variables));
    }

    @PutMapping("/approve/{taskId}")
    public ApiResponse<Void> approve(@PathVariable String taskId,
                                     @RequestParam String comment,
                                     @RequestParam boolean approved) {
        workflowService.approveTask(taskId, comment, approved);
        return ApiResponse.success();
    }

    @GetMapping("/tasks")
    public ApiResponse<List<Map<String, Object>>> pendingTasks(@RequestParam String assignee) {
        return ApiResponse.success(workflowService.getPendingTasks(assignee));
    }

    @GetMapping("/log/{businessId}")
    public ApiResponse<List<Map<String, Object>>> processLog(@PathVariable String businessId) {
        return ApiResponse.success(workflowService.getProcessLog(businessId));
    }
}
