package com.bank.updg.updg_workflow.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import com.bank.updg.updg_workflow.mapper.ProcessConfigMapper;
import com.bank.updg.updg_workflow.model.entity.ProcessDefinition;
import com.bank.updg.updg_workflow.service.ProcessConfigService;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
import java.util.List;
import java.util.UUID;

@Service
public class ProcessConfigServiceImpl
        extends ServiceImpl<ProcessConfigMapper, ProcessDefinition>
        implements ProcessConfigService {

    @Override
    public ProcessDefinition createConfig(ProcessDefinition config) {
        config.setId(UUID.randomUUID().toString().replace("-", ""));
        config.setVersion(1);
        config.setCreatedAt(LocalDateTime.now());
        config.setUpdatedAt(LocalDateTime.now());
        save(config);
        return config;
    }

    @Override
    public ProcessDefinition updateConfig(String id, ProcessDefinition config) {
        ProcessDefinition existing = getById(id);
        if (existing != null) {
            config.setId(id);
            config.setVersion(existing.getVersion() + 1);
            config.setUpdatedAt(LocalDateTime.now());
            updateById(config);
            return config;
        }
        return null;
    }

    @Override
    public List<ProcessDefinition> listAll() {
        return list();
    }

    @Override
    public ProcessDefinition getByKey(String processKey) {
        LambdaQueryWrapper<ProcessDefinition> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(ProcessDefinition::getProcessKey, processKey)
                .orderByDesc(ProcessDefinition::getVersion)
                .last("LIMIT 1");
        return getOne(wrapper);
    }

    @Override
    public void deleteConfig(String id) {
        removeById(id);
    }
}
