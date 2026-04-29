package com.bank.updg.updg_resource.controller;

import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.bank.updg.common.model.ApiResponse;
import com.bank.updg.updg_resource.model.entity.PersonnelReplacement;
import com.bank.updg.updg_resource.service.PersonnelReplacementService;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/resource/replacement")
@RequiredArgsConstructor
public class PersonnelReplacementController {

    private final PersonnelReplacementService replacementService;

    @PostMapping
    public ApiResponse<PersonnelReplacement> create(@RequestBody PersonnelReplacement data) {
        return ApiResponse.success(replacementService.createReplacement(data));
    }

    @PutMapping("/{id}")
    public ApiResponse<Void> update(@PathVariable String id, @RequestBody PersonnelReplacement data) {
        replacementService.updateReplacement(id, data);
        return ApiResponse.success();
    }

    @GetMapping("/{id}")
    public ApiResponse<PersonnelReplacement> getDetail(@PathVariable String id) {
        return ApiResponse.success(replacementService.getReplacement(id));
    }

    @GetMapping("/list")
    public ApiResponse<Page<PersonnelReplacement>> list(
            @RequestParam(required = false) String projectId,
            @RequestParam(required = false) String status,
            @RequestParam(defaultValue = "1") int page,
            @RequestParam(defaultValue = "10") int size) {
        return ApiResponse.success(replacementService.listReplacements(projectId, status, page, size));
    }

    @PostMapping("/{id}/approve")
    public ApiResponse<Void> approve(@PathVariable String id) {
        replacementService.approveReplacement(id);
        return ApiResponse.success();
    }

    @PostMapping("/{id}/complete")
    public ApiResponse<Void> complete(@PathVariable String id) {
        replacementService.completeReplacement(id);
        return ApiResponse.success();
    }
}
