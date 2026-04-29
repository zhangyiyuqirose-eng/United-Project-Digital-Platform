package com.bank.updg.updg_project.controller;

import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.bank.updg.common.model.ApiResponse;
import com.bank.updg.updg_project.model.entity.PreInitiation;
import com.bank.updg.updg_project.service.PreInitiationService;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

import java.util.Map;

@RestController
@RequestMapping("/api/project/pre-init")
@RequiredArgsConstructor
public class PreInitiationController {

    private final PreInitiationService preInitiationService;

    @PostMapping
    public ApiResponse<PreInitiation> create(@RequestBody PreInitiation data) {
        return ApiResponse.success(preInitiationService.createPreInitiation(data));
    }

    @PutMapping("/{id}/submit")
    public ApiResponse<Void> submit(@PathVariable String id) {
        preInitiationService.submitPreInitiation(id);
        return ApiResponse.success();
    }

    @PutMapping("/{id}/approve")
    public ApiResponse<Void> approve(@PathVariable String id,
                                     @RequestParam boolean approved,
                                     @RequestParam(required = false) String comment) {
        preInitiationService.approvePreInitiation(id, approved, comment);
        return ApiResponse.success();
    }

    @GetMapping("/{id}")
    public ApiResponse<PreInitiation> getDetail(@PathVariable String id) {
        return ApiResponse.success(preInitiationService.getPreInitiation(id));
    }

    @GetMapping("/dept/{deptId}")
    public ApiResponse<Page<PreInitiation>> listByDept(
            @PathVariable String deptId,
            @RequestParam(required = false) String status,
            @RequestParam(defaultValue = "1") int page,
            @RequestParam(defaultValue = "10") int size) {
        return ApiResponse.success(preInitiationService.listByDept(deptId, status, page, size));
    }
}
