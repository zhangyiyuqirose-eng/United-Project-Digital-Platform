package com.bank.updg.updg_resource.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.bank.updg.updg_resource.mapper.ResourceOutsourcingMapper;
import com.bank.updg.updg_resource.model.entity.ResourceOutsourcing;
import com.bank.updg.updg_resource.service.ResourceOutsourcingService;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
import java.util.List;

@Service
@RequiredArgsConstructor
public class ResourceOutsourcingServiceImpl implements ResourceOutsourcingService {

    private final ResourceOutsourcingMapper outsourcingMapper;

    @Override
    public Page<ResourceOutsourcing> listByPool(String pool, int page, int size) {
        Page<ResourceOutsourcing> pageObj = new Page<>(page, size);
        LambdaQueryWrapper<ResourceOutsourcing> wrapper = new LambdaQueryWrapper<>();
        if (pool != null && !pool.isBlank()) {
            wrapper.eq(ResourceOutsourcing::getResourcePool, pool);
        }
        wrapper.eq(ResourceOutsourcing::getStatus, "ACTIVE");
        return outsourcingMapper.selectPage(pageObj, wrapper);
    }

    @Override
    public ResourceOutsourcing getById(String staffId) {
        return outsourcingMapper.selectById(staffId);
    }

    @Override
    public void add(ResourceOutsourcing resource) {
        resource.setStatus("ACTIVE");
        resource.setCreateTime(LocalDateTime.now());
        resource.setUpdateTime(LocalDateTime.now());
        outsourcingMapper.insert(resource);
    }

    @Override
    public void update(ResourceOutsourcing resource) {
        resource.setUpdateTime(LocalDateTime.now());
        outsourcingMapper.updateById(resource);
    }

    @Override
    public void exitStaff(String staffId) {
        ResourceOutsourcing existing = outsourcingMapper.selectById(staffId);
        if (existing == null) {
            throw new IllegalArgumentException("人员不存在: " + staffId);
        }
        existing.setStatus("EXITED");
        existing.setExitTime(LocalDateTime.now());
        existing.setUpdateTime(LocalDateTime.now());
        outsourcingMapper.updateById(existing);
    }

    @Override
    public List<ResourceOutsourcing> listActiveBySkill(String skill) {
        LambdaQueryWrapper<ResourceOutsourcing> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(ResourceOutsourcing::getStatus, "ACTIVE")
               .like(ResourceOutsourcing::getSkill, skill);
        return outsourcingMapper.selectList(wrapper);
    }

    @Override
    public int countActiveByPool(String pool) {
        LambdaQueryWrapper<ResourceOutsourcing> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(ResourceOutsourcing::getResourcePool, pool)
               .eq(ResourceOutsourcing::getStatus, "ACTIVE");
        return Math.toIntExact(outsourcingMapper.selectCount(wrapper));
    }
}
