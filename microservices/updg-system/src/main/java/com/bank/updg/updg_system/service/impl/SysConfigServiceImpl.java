package com.bank.updg.updg_system.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.bank.updg.common.exception.BusinessException;
import com.bank.updg.common.model.enums.ErrorCodeEnum;
import com.bank.updg.updg_system.mapper.SysConfigMapper;
import com.bank.updg.updg_system.model.entity.SysConfig;
import com.bank.updg.updg_system.service.SysConfigService;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
import java.util.List;

@Service
@RequiredArgsConstructor
public class SysConfigServiceImpl extends com.baomidou.mybatisplus.extension.service.impl.ServiceImpl<SysConfigMapper, SysConfig> implements SysConfigService {

    @Override
    public SysConfig getConfig(String key) {
        return getOne(new LambdaQueryWrapper<SysConfig>()
                .eq(SysConfig::getConfigKey, key));
    }

    @Override
    public void setConfig(String key, String value, String type, String description) {
        SysConfig existing = getConfig(key);
        if (existing != null) {
            existing.setConfigValue(value);
            existing.setUpdateTime(LocalDateTime.now());
            updateById(existing);
        } else {
            SysConfig config = SysConfig.builder()
                    .configKey(key)
                    .configValue(value)
                    .configType(type)
                    .description(description)
                    .createTime(LocalDateTime.now())
                    .updateTime(LocalDateTime.now())
                    .build();
            save(config);
        }
    }

    @Override
    public List<SysConfig> listConfigs(String type) {
        if (type == null || type.isBlank()) {
            return list();
        }
        return list(new LambdaQueryWrapper<SysConfig>()
                .eq(SysConfig::getConfigType, type)
                .orderByAsc(SysConfig::getConfigKey));
    }

    @Override
    public void deleteConfig(Long configId) {
        SysConfig config = getById(configId);
        if (config == null) {
            throw new BusinessException(ErrorCodeEnum.NOT_FOUND, "Config not found: id=" + configId);
        }
        removeById(configId);
    }
}
