package com.bank.updg.updg_system.service.impl;

import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import com.bank.updg.updg_system.mapper.SysRoleMapper;
import com.bank.updg.updg_system.model.entity.SysRole;
import com.bank.updg.updg_system.service.SysRoleService;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
@RequiredArgsConstructor
public class SysRoleServiceImpl extends ServiceImpl<SysRoleMapper, SysRole> implements SysRoleService {

    @Override
    public void createRole(SysRole role) {
        save(role);
    }

    @Override
    public void updateRole(SysRole role) {
        updateById(role);
    }

    @Override
    public void deleteRole(String roleId) {
        removeById(roleId);
    }

    @Override
    public void assignPermissions(String roleId, List<String> permissionIds) {
        // TODO: insert into pm_sys_role_permission
    }

    @Override
    public List<String> getPermissionIds(String roleId) {
        // TODO: query from pm_sys_role_permission
        return List.of();
    }

    @Override
    public List<String> getRolesByUserId(String userId) {
        // TODO: query from pm_sys_user_role + pm_sys_role
        return List.of();
    }
}
