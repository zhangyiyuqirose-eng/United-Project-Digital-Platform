package com.bank.updg.updg_project.controller;

import com.bank.updg.common.model.ApiResponse;
import com.bank.updg.updg_project.model.entity.BuildRecord;
import com.bank.updg.updg_project.service.BuildRecordService;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

import java.util.List;

/**
 * F-702: CI/CD pipeline build tracking.
 */
@RestController
@RequestMapping("/api/project/build")
@RequiredArgsConstructor
public class BuildRecordController {

    private final BuildRecordService buildRecordService;

    @PostMapping
    public ApiResponse<BuildRecord> record(@RequestBody BuildRecord record) {
        return ApiResponse.success(buildRecordService.recordBuild(record));
    }

    @GetMapping("/project/{projectId}")
    public ApiResponse<List<BuildRecord>> getByProject(@PathVariable String projectId) {
        return ApiResponse.success(buildRecordService.getByProjectId(projectId));
    }
}
