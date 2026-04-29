package com.bank.updg.updg_system.service;

import com.baomidou.mybatisplus.extension.service.IService;
import com.bank.updg.updg_system.model.entity.SysAuditLog;

public interface SysAuditLogService extends IService<SysAuditLog> {

    void recordAuditLog(String userId, String module, String operation,
                        String ipAddress, String requestUri,
                        String requestBody, String responseCode,
                        String beforeValue, String afterValue);
}
