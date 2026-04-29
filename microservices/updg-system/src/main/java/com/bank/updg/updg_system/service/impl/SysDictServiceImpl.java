package com.bank.updg.updg_system.service.impl;

import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import com.bank.updg.updg_system.mapper.SysDictMapper;
import com.bank.updg.updg_system.model.entity.SysDict;
import com.bank.updg.updg_system.service.SysDictService;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.util.Map;

@Service
@RequiredArgsConstructor
public class SysDictServiceImpl extends ServiceImpl<SysDictMapper, SysDict> implements SysDictService {

    @Override
    public Map<String, Object> getDictByCode(String dictCode) {
        // TODO: load from Redis cache, fallback to DB
        return Map.of();
    }

    @Override
    public void refreshCache(String dictCode) {
        // TODO: evict Redis cache for this dict
    }
}
