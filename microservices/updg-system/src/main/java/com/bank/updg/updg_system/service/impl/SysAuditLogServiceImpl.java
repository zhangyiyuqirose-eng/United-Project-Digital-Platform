package com.bank.updg.updg_system.service.impl;

import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import com.bank.updg.updg_system.mapper.SysAuditLogMapper;
import com.bank.updg.updg_system.model.entity.SysAuditLog;
import com.bank.updg.updg_system.service.SysAuditLogService;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.util.UUID;

@Service
@RequiredArgsConstructor
public class SysAuditLogServiceImpl extends ServiceImpl<SysAuditLogMapper, SysAuditLog> implements SysAuditLogService {

    @Override
    public void recordAuditLog(String userId, String module, String operation,
                               String ipAddress, String requestUri,
                               String requestBody, String responseCode,
                               String beforeValue, String afterValue) {
        SysAuditLog log = new SysAuditLog();
        log.setAuditId(UUID.randomUUID().toString().replace("-", ""));
        log.setUserId(userId);
        log.setModule(module);
        log.setOperation(operation);
        log.setIpAddress(ipAddress);
        log.setRequestUri(requestUri);
        log.setRequestBody(requestBody);
        log.setResponseCode(responseCode);
        log.setBeforeValue(beforeValue);
        log.setAfterValue(afterValue);
        save(log);
    }
}
