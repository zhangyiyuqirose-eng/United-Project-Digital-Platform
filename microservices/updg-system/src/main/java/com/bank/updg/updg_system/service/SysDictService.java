package com.bank.updg.updg_system.service;

import com.baomidou.mybatisplus.extension.service.IService;
import com.bank.updg.updg_system.model.entity.SysDict;

import java.util.Map;

public interface SysDictService extends IService<SysDict> {

    Map<String, Object> getDictByCode(String dictCode);

    void refreshCache(String dictCode);
}
