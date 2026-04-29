package com.bank.updg.updg_system.service;

import com.baomidou.mybatisplus.extension.service.IService;
import com.bank.updg.updg_system.model.entity.SysRole;

import java.util.List;

public interface SysRoleService extends IService<SysRole> {

    void createRole(SysRole role);

    void updateRole(SysRole role);

    void deleteRole(String roleId);

    void assignPermissions(String roleId, List<String> permissionIds);

    List<String> getPermissionIds(String roleId);

    List<String> getRolesByUserId(String userId);
}
