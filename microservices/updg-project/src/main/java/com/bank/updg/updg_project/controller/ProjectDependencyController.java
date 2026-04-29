package com.bank.updg.updg_project.controller;

import com.bank.updg.common.model.ApiResponse;
import com.bank.updg.updg_project.model.entity.ProjectDependency;
import com.bank.updg.updg_project.service.ProjectDependencyService;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

import java.util.List;

/**
 * F-602: Cross-project dependency management.
 */
@RestController
@RequestMapping("/api/project/dependency")
@RequiredArgsConstructor
public class ProjectDependencyController {

    private final ProjectDependencyService dependencyService;

    @PostMapping
    public ApiResponse<ProjectDependency> create(@RequestBody ProjectDependency dependency) {
        return ApiResponse.success(dependencyService.createDependency(dependency));
    }

    @GetMapping("/project/{projectId}")
    public ApiResponse<List<ProjectDependency>> getByProject(@PathVariable String projectId) {
        return ApiResponse.success(dependencyService.getByProjectId(projectId));
    }

    @DeleteMapping("/{id}")
    public ApiResponse<Void> remove(@PathVariable String id) {
        dependencyService.removeDependency(id);
        return ApiResponse.success();
    }
}
