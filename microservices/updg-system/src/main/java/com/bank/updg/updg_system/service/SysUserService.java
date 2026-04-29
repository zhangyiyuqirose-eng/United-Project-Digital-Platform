package com.bank.updg.updg_system.service;

import com.baomidou.mybatisplus.extension.service.IService;
import com.bank.updg.updg_system.model.entity.SysUser;

import java.util.List;

public interface SysUserService extends IService<SysUser> {

    SysUser getByUsername(String username);

    void createUser(SysUser user);

    void updateUser(SysUser user);

    void deleteUser(String userId);

    List<SysUser> listByDept(String deptId);

    boolean hasRole(String userId, String roleCode);
}
