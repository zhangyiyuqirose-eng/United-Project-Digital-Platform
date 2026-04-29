package com.bank.updg.updg_project.controller;

import com.bank.updg.common.model.ApiResponse;
import com.bank.updg.updg_project.model.entity.ProjectTask;
import com.bank.updg.updg_project.service.CriticalPathService;
import com.bank.updg.updg_project.service.TaskService;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/project/task")
@RequiredArgsConstructor
public class TaskController {

    private final TaskService taskService;
    private final CriticalPathService criticalPathService;

    @PostMapping
    public ApiResponse createTask(@RequestBody ProjectTask task) {
        return ApiResponse.success(taskService.createTask(task));
    }

    @PutMapping("/{taskId}")
    public ApiResponse updateTask(@PathVariable String taskId, @RequestBody ProjectTask task) {
        taskService.updateTask(taskId, task);
        return ApiResponse.success("Task updated");
    }

    @GetMapping("/{taskId}")
    public ApiResponse getTask(@PathVariable String taskId) {
        return ApiResponse.success(taskService.getTask(taskId));
    }

    @GetMapping("/project/{projectId}")
    public ApiResponse listByProject(@PathVariable String projectId,
                                     @RequestParam(required = false) String status,
                                     @RequestParam(required = false) String assignee,
                                     @RequestParam(defaultValue = "1") int page,
                                     @RequestParam(defaultValue = "20") int size) {
        return ApiResponse.success(taskService.listByProject(projectId, status, assignee, page, size));
    }

    @GetMapping("/project/{projectId}/tree")
    public ApiResponse getTaskTree(@PathVariable String projectId) {
        return ApiResponse.success(taskService.getTaskTree(projectId));
    }

    @PutMapping("/{taskId}/progress")
    public ApiResponse updateProgress(@PathVariable String taskId,
                                      @RequestParam int progress) {
        taskService.updateProgress(taskId, progress);
        return ApiResponse.success("Progress updated");
    }

    @PutMapping("/{taskId}/block")
    public ApiResponse blockTask(@PathVariable String taskId,
                                 @RequestParam String reason) {
        taskService.blockTask(taskId, reason);
        return ApiResponse.success("Task blocked");
    }

    @PutMapping("/{taskId}/complete")
    public ApiResponse completeTask(@PathVariable String taskId) {
        taskService.completeTask(taskId);
        return ApiResponse.success("Task completed");
    }

    @GetMapping("/project/{projectId}/overdue")
    public ApiResponse getOverdueTasks(@PathVariable String projectId) {
        return ApiResponse.success(taskService.getOverdueTasks(projectId));
    }

    @DeleteMapping("/{taskId}")
    public ApiResponse deleteTask(@PathVariable String taskId) {
        taskService.deleteTask(taskId);
        return ApiResponse.success("Task deleted");
    }

    /**
     * F-303: Critical path analysis.
     * Returns list of task IDs on the critical path.
     */
    @GetMapping("/project/{projectId}/critical-path")
    public ApiResponse<List<String>> getCriticalPath(@PathVariable String projectId) {
        return ApiResponse.success(criticalPathService.findCriticalPath(projectId));
    }

    /**
     * F-308: Task dependency adjacency list.
     * Returns map of taskId -> list of predecessor task IDs.
     */
    @GetMapping("/project/{projectId}/dependencies")
    public ApiResponse<Map<String, List<String>>> getDependencies(@PathVariable String projectId) {
        return ApiResponse.success(taskService.getDependencies(projectId));
    }

    /**
     * F-308: Impact analysis.
     * Returns all downstream tasks affected by this task's delay.
     */
    @GetMapping("/{taskId}/impact")
    public ApiResponse<List<String>> getImpact(@PathVariable String taskId) {
        return ApiResponse.success(taskService.getDownstreamTasks(taskId));
    }
}
