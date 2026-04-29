package com.bank.updg.updg_workflow.mapper;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.bank.updg.updg_workflow.model.entity.ProcessDefinition;
import org.apache.ibatis.annotations.Mapper;

@Mapper
public interface ProcessConfigMapper extends BaseMapper<ProcessDefinition> {
}
