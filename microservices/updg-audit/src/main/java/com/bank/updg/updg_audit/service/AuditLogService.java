package com.bank.updg.updg_audit.service;

import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.baomidou.mybatisplus.extension.service.IService;
import com.bank.updg.updg_audit.model.entity.AuditLogEntry;

public interface AuditLogService extends IService<AuditLogEntry> {

    void recordLog(AuditLogEntry logEntry);

    Page<AuditLogEntry> getLogsByUser(String userId, int page, int size);

    Page<AuditLogEntry> getLogsByModule(String module, int page, int size);

    Page<AuditLogEntry> getLogsByAction(String action, int page, int size);

    Page<AuditLogEntry> getLogsByDateRange(String from, String to, int page, int size);

    AuditLogEntry getLogDetail(String logId);

    byte[] exportLogs(String userId, String module, String from, String to);
}
