package com.bank.updg.updg_audit.model.entity;

import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
@TableName("pm_audit_log")
public class AuditLogEntry {
    @TableId
    private String logId;
    private String userId;
    private String userName;
    private String userIp;
    private String action;
    private String module;
    private String entityType;
    private String entityId;
    private String oldValue;
    private String newValue;
    private String result;
    private String timestamp;
    private String traceId;
}
