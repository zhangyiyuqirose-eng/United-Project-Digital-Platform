package com.bank.updg.updg_audit.mapper;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.bank.updg.updg_audit.model.entity.AuditLogEntry;
import org.apache.ibatis.annotations.Mapper;

@Mapper
public interface AuditLogEntryMapper extends BaseMapper<AuditLogEntry> {
}
