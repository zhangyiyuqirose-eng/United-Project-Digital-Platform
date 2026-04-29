package com.bank.updg.updg_project.controller;

import com.bank.updg.common.model.ApiResponse;
import com.bank.updg.updg_project.model.entity.CodeRepo;
import com.bank.updg.updg_project.service.CodeRepoService;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

import java.util.List;

/**
 * F-701: Code repository integration tracking.
 */
@RestController
@RequestMapping("/api/project/code-repo")
@RequiredArgsConstructor
public class CodeRepoController {

    private final CodeRepoService codeRepoService;

    @PostMapping
    public ApiResponse<CodeRepo> register(@RequestBody CodeRepo repo) {
        return ApiResponse.success(codeRepoService.registerRepo(repo));
    }

    @GetMapping("/project/{projectId}")
    public ApiResponse<List<CodeRepo>> getByProject(@PathVariable String projectId) {
        return ApiResponse.success(codeRepoService.getByProjectId(projectId));
    }

    @PostMapping("/{repoId}/sync")
    public ApiResponse<Void> sync(@PathVariable String repoId) {
        codeRepoService.syncRepo(repoId);
        return ApiResponse.success();
    }
}
