package com.bank.updg.updg_system.controller;

import com.bank.updg.common.model.ApiResponse;
import com.bank.updg.updg_system.model.entity.SysRole;
import com.bank.updg.updg_system.service.SysRoleService;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/system/role")
@RequiredArgsConstructor
public class SysRoleController {

    private final SysRoleService roleService;

    @GetMapping("/list")
    public ApiResponse<List<SysRole>> listPage(
            @RequestParam(defaultValue = "1") int page,
            @RequestParam(defaultValue = "10") int limit,
            @RequestParam(required = false) String keyword) {
        return ApiResponse.success(roleService.list());
    }

    @GetMapping("/all")
    public ApiResponse<List<SysRole>> listAll() {
        return ApiResponse.success(roleService.list());
    }

    @GetMapping
    public ApiResponse<List<SysRole>> all() {
        return ApiResponse.success(roleService.list());
    }

    @PostMapping
    public ApiResponse<Void> create(@RequestBody SysRole role) {
        roleService.createRole(role);
        return ApiResponse.success();
    }

    @PutMapping("/{id}")
    public ApiResponse<Void> update(@PathVariable String id, @RequestBody SysRole role) {
        role.setRoleId(id);
        roleService.updateRole(role);
        return ApiResponse.success();
    }

    @DeleteMapping("/{id}")
    public ApiResponse<Void> delete(@PathVariable String id) {
        roleService.deleteRole(id);
        return ApiResponse.success();
    }

    @PostMapping("/{id}/permissions")
    public ApiResponse<Void> assignPermissions(@PathVariable String id,
                                               @RequestBody List<String> permissionIds) {
        roleService.assignPermissions(id, permissionIds);
        return ApiResponse.success();
    }
}
