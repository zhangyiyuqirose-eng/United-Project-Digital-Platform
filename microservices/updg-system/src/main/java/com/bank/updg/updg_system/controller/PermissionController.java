package com.bank.updg.updg_system.controller;

import com.bank.updg.common.model.ApiResponse;
import com.bank.updg.updg_system.model.entity.SysPermission;
import com.bank.updg.updg_system.service.PermissionService;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

import java.util.List;

/**
 * Permission management API.
 */
@RestController
@RequestMapping("/api/system/permission")
@RequiredArgsConstructor
public class PermissionController {

    private final PermissionService permissionService;

    /**
     * List all permissions (flat).
     */
    @GetMapping
    public ApiResponse<List<SysPermission>> list() {
        return ApiResponse.success(permissionService.list());
    }

    /**
     * Get permission tree (hierarchical by parentId).
     */
    @GetMapping("/tree")
    public ApiResponse<List<SysPermission>> tree() {
        return ApiResponse.success(permissionService.getPermissionTree());
    }

    /**
     * Create a new permission.
     */
    @PostMapping
    public ApiResponse<Void> create(@RequestBody SysPermission permission) {
        permissionService.save(permission);
        return ApiResponse.success();
    }

    /**
     * Update an existing permission.
     */
    @PutMapping("/{id}")
    public ApiResponse<Void> update(@PathVariable String id,
                                    @RequestBody SysPermission permission) {
        permission.setPermissionId(id);
        permissionService.updateById(permission);
        return ApiResponse.success();
    }

    /**
     * Delete a permission.
     */
    @DeleteMapping("/{id}")
    public ApiResponse<Void> delete(@PathVariable String id) {
        permissionService.removeById(id);
        return ApiResponse.success();
    }

    /**
     * Get permissions assigned to a specific role.
     */
    @GetMapping("/role/{roleId}")
    public ApiResponse<List<SysPermission>> getByRole(@PathVariable String roleId) {
        return ApiResponse.success(permissionService.getPermissionsByRoleId(roleId));
    }
}
