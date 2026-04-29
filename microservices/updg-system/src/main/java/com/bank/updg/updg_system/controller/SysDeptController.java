package com.bank.updg.updg_system.controller;

import com.bank.updg.common.model.ApiResponse;
import com.bank.updg.updg_system.model.entity.SysDept;
import com.bank.updg.updg_system.service.SysDeptService;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/system/dept")
@RequiredArgsConstructor
public class SysDeptController {

    private final SysDeptService deptService;

    @GetMapping
    public ApiResponse<List<SysDept>> list() {
        return ApiResponse.success(deptService.listTree());
    }

    @GetMapping("/{id}")
    public ApiResponse<SysDept> getById(@PathVariable String id) {
        return ApiResponse.success(deptService.getById(id));
    }

    @PostMapping
    public ApiResponse<Void> create(@RequestBody SysDept dept) {
        deptService.createDept(dept);
        return ApiResponse.success();
    }

    @PutMapping("/{id}")
    public ApiResponse<Void> update(@PathVariable String id, @RequestBody SysDept dept) {
        dept.setDeptId(id);
        deptService.updateDept(dept);
        return ApiResponse.success();
    }

    @DeleteMapping("/{id}")
    public ApiResponse<Void> delete(@PathVariable String id) {
        deptService.deleteDept(id);
        return ApiResponse.success();
    }
}
