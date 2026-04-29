package com.bank.updg.updg_system.controller;

import java.util.List;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.bank.updg.common.model.ApiResponse;
import com.bank.updg.updg_system.model.entity.SysUser;
import com.bank.updg.updg_system.service.SysUserService;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/system/user")
@RequiredArgsConstructor
public class SysUserController {

    private final SysUserService userService;

    @GetMapping("/list")
    public ApiResponse<Page<SysUser>> list(
            @RequestParam(defaultValue = "1") int page,
            @RequestParam(defaultValue = "10") int limit,
            @RequestParam(required = false) String deptId,
            @RequestParam(required = false) String keyword,
            @RequestParam(required = false) Integer status) {
        Page<SysUser> pageObj = new Page<>(page, limit);
        if (deptId != null) {
            return ApiResponse.success(userService.page(pageObj,
                    new LambdaQueryWrapper<SysUser>().eq(SysUser::getDeptId, deptId)));
        }
        return ApiResponse.success(userService.page(pageObj));
    }

    @GetMapping
    public ApiResponse<List<SysUser>> all() {
        return ApiResponse.success(userService.list());
    }

    @GetMapping("/{id}")
    public ApiResponse<SysUser> getById(@PathVariable String id) {
        return ApiResponse.success(userService.getById(id));
    }

    @PostMapping
    public ApiResponse<Void> create(@RequestBody SysUser user) {
        userService.createUser(user);
        return ApiResponse.success();
    }

    @PutMapping("/{id}")
    public ApiResponse<Void> update(@PathVariable String id, @RequestBody SysUser user) {
        user.setUserId(id);
        userService.updateUser(user);
        return ApiResponse.success();
    }

    @DeleteMapping("/{id}")
    public ApiResponse<Void> delete(@PathVariable String id) {
        userService.deleteUser(id);
        return ApiResponse.success();
    }
}
