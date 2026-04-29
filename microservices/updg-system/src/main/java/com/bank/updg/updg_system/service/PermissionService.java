package com.bank.updg.updg_system.service;

import com.baomidou.mybatisplus.extension.service.IService;
import com.bank.updg.updg_system.model.entity.SysPermission;

import java.util.List;

/**
 * Permission management service.
 */
public interface PermissionService extends IService<SysPermission> {

    /**
     * Build hierarchical permission tree from flat list.
     */
    List<SysPermission> getPermissionTree();

    /**
     * Get permissions assigned to a specific role.
     */
    List<SysPermission> getPermissionsByRoleId(String roleId);
}
