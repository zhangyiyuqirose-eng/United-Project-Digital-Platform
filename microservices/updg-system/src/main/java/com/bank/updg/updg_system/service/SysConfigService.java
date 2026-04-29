package com.bank.updg.updg_system.service;

import com.baomidou.mybatisplus.extension.service.IService;
import com.bank.updg.updg_system.model.entity.SysConfig;

import java.util.List;

public interface SysConfigService extends IService<SysConfig> {

    /**
     * Get configuration by key
     */
    SysConfig getConfig(String key);

    /**
     * Set or update a configuration value
     */
    void setConfig(String key, String value, String type, String description);

    /**
     * List configurations by type
     */
    List<SysConfig> listConfigs(String type);

    /**
     * Delete a configuration by ID
     */
    void deleteConfig(Long configId);
}
