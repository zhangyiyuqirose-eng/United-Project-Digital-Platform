package com.bank.updg.updg_resource.service;

import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.bank.updg.updg_resource.model.entity.ResourcePool;

import java.util.List;

public interface ResourcePoolService {

    List<ResourcePool> listAll();

    ResourcePool getById(String poolId);

    void create(ResourcePool pool);

    void update(ResourcePool pool);
}
