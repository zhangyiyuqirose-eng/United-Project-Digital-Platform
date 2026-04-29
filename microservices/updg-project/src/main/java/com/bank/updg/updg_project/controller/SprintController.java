package com.bank.updg.updg_project.controller;

import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.bank.updg.common.model.ApiResponse;
import com.bank.updg.updg_project.model.entity.Sprint;
import com.bank.updg.updg_project.service.SprintService;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

import java.math.BigDecimal;
import java.util.List;

/**
 * Sprint management endpoints (F-309).
 */
@RestController
@RequestMapping("/api/project/sprint")
@RequiredArgsConstructor
public class SprintController {

    private final SprintService sprintService;

    @PostMapping
    public ApiResponse<Sprint> createSprint(@RequestBody Sprint sprint) {
        return ApiResponse.success(sprintService.createSprint(sprint));
    }

    @PutMapping("/{sprintId}")
    public ApiResponse<Void> updateSprint(@PathVariable String sprintId, @RequestBody Sprint sprint) {
        sprintService.updateSprint(sprintId, sprint);
        return ApiResponse.success();
    }

    @GetMapping("/{sprintId}")
    public ApiResponse<Sprint> getSprint(@PathVariable String sprintId) {
        return ApiResponse.success(sprintService.getSprint(sprintId));
    }

    @GetMapping("/project/{projectId}")
    public ApiResponse<List<Sprint>> listByProject(@PathVariable String projectId) {
        return ApiResponse.success(sprintService.listByProject(projectId));
    }

    @GetMapping("/project/{projectId}/page")
    public ApiResponse<Page<Sprint>> pageByProject(@PathVariable String projectId,
                                                   @RequestParam(defaultValue = "1") int page,
                                                   @RequestParam(defaultValue = "10") int size) {
        return ApiResponse.success(sprintService.pageByProject(projectId, page, size));
    }

    @PutMapping("/{sprintId}/complete")
    public ApiResponse<Void> completeSprint(@PathVariable String sprintId,
                                            @RequestParam(required = false) BigDecimal velocity) {
        sprintService.completeSprint(sprintId, velocity != null ? velocity : BigDecimal.ZERO);
        return ApiResponse.success();
    }

    @PutMapping("/{sprintId}/cancel")
    public ApiResponse<Void> cancelSprint(@PathVariable String sprintId) {
        sprintService.cancelSprint(sprintId);
        return ApiResponse.success();
    }

    @GetMapping("/project/{projectId}/active")
    public ApiResponse<Sprint> getActiveSprint(@PathVariable String projectId) {
        return ApiResponse.success(sprintService.getActiveSprint(projectId));
    }
}
