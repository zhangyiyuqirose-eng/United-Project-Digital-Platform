package com.bank.updg.updg_system.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import com.bank.updg.common.exception.BusinessException;
import com.bank.updg.common.model.enums.ErrorCodeEnum;
import com.bank.updg.updg_system.mapper.SysUserMapper;
import com.bank.updg.updg_system.model.entity.SysUser;
import com.bank.updg.updg_system.service.SysUserService;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
@RequiredArgsConstructor
public class SysUserServiceImpl extends ServiceImpl<SysUserMapper, SysUser> implements SysUserService {

    @Override
    public SysUser getByUsername(String username) {
        return getOne(new LambdaQueryWrapper<SysUser>().eq(SysUser::getUsername, username));
    }

    @Override
    public void createUser(SysUser user) {
        if (getByUsername(user.getUsername()) != null) {
            throw new BusinessException(ErrorCodeEnum.DUPLICATE, "用户名已存在");
        }
        save(user);
    }

    @Override
    public void updateUser(SysUser user) {
        updateById(user);
    }

    @Override
    public void deleteUser(String userId) {
        SysUser user = getById(userId);
        if (user == null) {
            throw new BusinessException(ErrorCodeEnum.USER_NOT_FOUND);
        }
        removeById(userId);
    }

    @Override
    public List<SysUser> listByDept(String deptId) {
        return list(new LambdaQueryWrapper<SysUser>().eq(SysUser::getDeptId, deptId));
    }

    @Override
    public boolean hasRole(String userId, String roleCode) {
        // Simplified: check via user-role join
        return false;
    }
}
