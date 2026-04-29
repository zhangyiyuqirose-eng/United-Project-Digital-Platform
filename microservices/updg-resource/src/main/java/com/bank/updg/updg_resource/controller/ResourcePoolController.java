package com.bank.updg.updg_resource.controller;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.bank.updg.common.model.ApiResponse;
import com.bank.updg.updg_resource.mapper.ResourcePoolMapper;
import com.bank.updg.updg_resource.model.entity.ResourcePool;
import com.bank.updg.updg_resource.service.ResourcePoolService;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/resource/pool")
@RequiredArgsConstructor
public class ResourcePoolController {

    private final ResourcePoolService poolService;
    private final ResourcePoolMapper poolMapper;

    @GetMapping("/list")
    public ApiResponse<Page<ResourcePool>> listPage(
            @RequestParam(defaultValue = "1") int page,
            @RequestParam(defaultValue = "10") int limit,
            @RequestParam(required = false) String keyword,
            @RequestParam(required = false) String status) {
        Page<ResourcePool> pageObj = new Page<>(page, limit);
        return ApiResponse.success(poolMapper.selectPage(pageObj, new LambdaQueryWrapper<ResourcePool>()));
    }

    @GetMapping
    public ApiResponse<List<ResourcePool>> listAll() {
        return ApiResponse.success(poolService.listAll());
    }

    @GetMapping("/{poolId}")
    public ApiResponse getById(@PathVariable String poolId) {
        return ApiResponse.success(poolService.getById(poolId));
    }

    @PostMapping
    public ApiResponse create(@RequestBody ResourcePool pool) {
        poolService.create(pool);
        return ApiResponse.success("创建成功");
    }

    @PutMapping("/{poolId}")
    public ApiResponse update(@PathVariable String poolId, @RequestBody ResourcePool pool) {
        pool.setPoolId(poolId);
        poolService.update(pool);
        return ApiResponse.success("更新成功");
    }
}
