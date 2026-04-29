package com.bank.updg.updg_audit.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import com.bank.updg.updg_audit.mapper.AuditLogEntryMapper;
import com.bank.updg.updg_audit.model.entity.AuditLogEntry;
import com.bank.updg.updg_audit.service.AuditLogService;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.nio.charset.StandardCharsets;

@Service
@RequiredArgsConstructor
public class AuditLogServiceImpl extends ServiceImpl<AuditLogEntryMapper, AuditLogEntry>
        implements AuditLogService {

    @Override
    public void recordLog(AuditLogEntry logEntry) {
        save(logEntry);
    }

    @Override
    public Page<AuditLogEntry> getLogsByUser(String userId, int page, int size) {
        Page<AuditLogEntry> pageObj = new Page<>(page, size);
        return page(pageObj, new LambdaQueryWrapper<AuditLogEntry>()
                .eq(AuditLogEntry::getUserId, userId)
                .orderByDesc(AuditLogEntry::getTimestamp));
    }

    @Override
    public Page<AuditLogEntry> getLogsByModule(String module, int page, int size) {
        Page<AuditLogEntry> pageObj = new Page<>(page, size);
        return page(pageObj, new LambdaQueryWrapper<AuditLogEntry>()
                .eq(AuditLogEntry::getModule, module)
                .orderByDesc(AuditLogEntry::getTimestamp));
    }

    @Override
    public Page<AuditLogEntry> getLogsByAction(String action, int page, int size) {
        Page<AuditLogEntry> pageObj = new Page<>(page, size);
        return page(pageObj, new LambdaQueryWrapper<AuditLogEntry>()
                .eq(AuditLogEntry::getAction, action)
                .orderByDesc(AuditLogEntry::getTimestamp));
    }

    @Override
    public Page<AuditLogEntry> getLogsByDateRange(String from, String to, int page, int size) {
        Page<AuditLogEntry> pageObj = new Page<>(page, size);
        return page(pageObj, new LambdaQueryWrapper<AuditLogEntry>()
                .ge(AuditLogEntry::getTimestamp, from)
                .le(AuditLogEntry::getTimestamp, to)
                .orderByDesc(AuditLogEntry::getTimestamp));
    }

    @Override
    public AuditLogEntry getLogDetail(String logId) {
        return getById(logId);
    }

    @Override
    public byte[] exportLogs(String userId, String module, String from, String to) {
        LambdaQueryWrapper<AuditLogEntry> wrapper = new LambdaQueryWrapper<AuditLogEntry>()
                .orderByDesc(AuditLogEntry::getTimestamp);
        if (userId != null) {
            wrapper.eq(AuditLogEntry::getUserId, userId);
        }
        if (module != null) {
            wrapper.eq(AuditLogEntry::getModule, module);
        }
        if (from != null) {
            wrapper.ge(AuditLogEntry::getTimestamp, from);
        }
        if (to != null) {
            wrapper.le(AuditLogEntry::getTimestamp, to);
        }

        java.util.List<AuditLogEntry> logs = list(wrapper);
        StringBuilder csv = new StringBuilder();
        csv.append("logId,userId,userName,userIp,action,module,entityType,entityId,result,timestamp,traceId\n");
        for (AuditLogEntry log : logs) {
            csv.append(log.getLogId()).append(",");
            csv.append(log.getUserId()).append(",");
            csv.append(log.getUserName()).append(",");
            csv.append(log.getUserIp()).append(",");
            csv.append(log.getAction()).append(",");
            csv.append(log.getModule()).append(",");
            csv.append(log.getEntityType()).append(",");
            csv.append(log.getEntityId()).append(",");
            csv.append(log.getResult()).append(",");
            csv.append(log.getTimestamp()).append(",");
            csv.append(log.getTraceId()).append("\n");
        }
        return csv.toString().getBytes(StandardCharsets.UTF_8);
    }
}
