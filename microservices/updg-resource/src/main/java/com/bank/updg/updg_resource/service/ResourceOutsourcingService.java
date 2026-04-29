package com.bank.updg.updg_resource.service;

import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.bank.updg.updg_resource.model.entity.ResourceOutsourcing;

import java.util.List;

public interface ResourceOutsourcingService {

    Page<ResourceOutsourcing> listByPool(String pool, int page, int size);

    ResourceOutsourcing getById(String staffId);

    void add(ResourceOutsourcing resource);

    void update(ResourceOutsourcing resource);

    void exitStaff(String staffId);

    List<ResourceOutsourcing> listActiveBySkill(String skill);

    int countActiveByPool(String pool);
}
