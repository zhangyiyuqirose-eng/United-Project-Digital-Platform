package com.bank.updg.updg_resource.service.impl;

import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.bank.updg.updg_resource.mapper.ResourcePoolMapper;
import com.bank.updg.updg_resource.model.entity.ResourcePool;
import com.bank.updg.updg_resource.service.ResourcePoolService;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
@RequiredArgsConstructor
public class ResourcePoolServiceImpl implements ResourcePoolService {

    private final ResourcePoolMapper poolMapper;

    @Override
    public List<ResourcePool> listAll() {
        return poolMapper.selectList(null);
    }

    @Override
    public ResourcePool getById(String poolId) {
        return poolMapper.selectById(poolId);
    }

    @Override
    public void create(ResourcePool pool) {
        poolMapper.insert(pool);
    }

    @Override
    public void update(ResourcePool pool) {
        poolMapper.updateById(pool);
    }
}
