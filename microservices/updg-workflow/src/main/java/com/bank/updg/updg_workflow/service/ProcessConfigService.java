package com.bank.updg.updg_workflow.service;

import com.baomidou.mybatisplus.extension.service.IService;
import com.bank.updg.updg_workflow.model.entity.ProcessDefinition;

import java.util.List;

public interface ProcessConfigService extends IService<ProcessDefinition> {

    ProcessDefinition createConfig(ProcessDefinition config);

    ProcessDefinition updateConfig(String id, ProcessDefinition config);

    List<ProcessDefinition> listAll();

    ProcessDefinition getByKey(String processKey);

    void deleteConfig(String id);
}
