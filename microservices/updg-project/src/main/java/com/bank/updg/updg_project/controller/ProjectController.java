package com.bank.updg.updg_project.controller;

import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.bank.updg.common.model.ApiResponse;
import com.bank.updg.updg_project.model.entity.Project;
import com.bank.updg.updg_project.service.HealthScoreService;
import com.bank.updg.updg_project.service.ProjectCloseService;
import com.bank.updg.updg_project.service.ProjectService;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

import java.math.BigDecimal;
import java.util.List;
import java.util.Map;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;

@RestController
@RequestMapping("/api/project")
@RequiredArgsConstructor
public class ProjectController {

    private final ProjectService projectService;
    private final HealthScoreService healthScoreService;
    private final ProjectCloseService projectCloseService;

    @GetMapping("/list")
    public ApiResponse<Page<Project>> list(
            @RequestParam(defaultValue = "1") int page,
            @RequestParam(defaultValue = "10") int limit,
            @RequestParam(required = false) String status,
            @RequestParam(required = false) String keyword) {
        Page<Project> pageObj = new Page<>(page, limit);
        return ApiResponse.success(projectService.page(pageObj));
    }

    @GetMapping
    public ApiResponse<List<Project>> all() {
        return ApiResponse.success(projectService.list());
    }

    @PostMapping("/init")
    public ApiResponse<Void> initProject(@RequestBody Project project) {
        projectService.initProject(project);
        return ApiResponse.success();
    }

    @PutMapping("/progress/{id}")
    public ApiResponse<Void> updateProgress(@PathVariable String id,
                                            @RequestParam String wbsJson) {
        projectService.updateProgress(id, wbsJson);
        return ApiResponse.success();
    }

    @GetMapping("/progress/{id}")
    public ApiResponse<Project> getProgress(@PathVariable String id) {
        return ApiResponse.success(projectService.getById(id));
    }

    @PostMapping("/change")
    public ApiResponse<Void> submitChange(@RequestBody Map<String, String> body) {
        projectService.submitChange(
                body.get("projectId"), body.get("changeType"),
                body.get("content"), body.get("reason"));
        return ApiResponse.success();
    }

    @PostMapping("/close")
    public ApiResponse<Void> closeProject(@RequestBody Map<String, String> body) {
        projectService.closeProject(
                body.get("projectId"), body.get("summary"),
                body.get("costSummary"), body.get("lessonsLearned"));
        return ApiResponse.success();
    }

    @GetMapping("/portfolio")
    public ApiResponse<Map<String, Object>> portfolio() {
        return ApiResponse.success(projectService.getPortfolio());
    }

    @PostMapping("/evm/{id}")
    public ApiResponse<Void> calculateEVM(@PathVariable String id,
                                          @RequestParam BigDecimal pv,
                                          @RequestParam BigDecimal ev,
                                          @RequestParam BigDecimal ac) {
        projectService.calculateEVM(id, pv, ev, ac);
        return ApiResponse.success();
    }

    /**
     * F-113: Compute and save project health score.
     */
    @PostMapping("/{id}/healthScore")
    public ApiResponse<BigDecimal> computeHealthScore(@PathVariable String id) {
        BigDecimal score = healthScoreService.computeHealthScore(id);
        Project project = projectService.getById(id);
        project.setHealthScore(score);
        projectService.updateById(project);
        return ApiResponse.success(score);
    }

    /**
     * F-406: Complete project close settlement.
     */
    @PostMapping("/close/{closeId}/complete")
    public ApiResponse<Void> completeClose(@PathVariable String closeId) {
        projectCloseService.completeClose(closeId);
        return ApiResponse.success();
    }

    /**
     * F-104: Rule-based WBS decomposition.
     * Generates a standard WBS tree based on common project phases:
     * Initiation, Planning, Execution, Testing, Delivery.
     */
    @PostMapping("/{id}/wbs/decompose")
    public ApiResponse<Map<String, Object>> decomposeWbs(@PathVariable String id) {
        Map<String, Object> wbs = projectService.generateWbs(id);
        return ApiResponse.success(wbs);
    }
}
