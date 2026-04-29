package com.bank.updg.updg_system.model.entity;

import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;

import java.time.LocalDateTime;

/**
 * 审计日志实体
 */
@Data
@TableName("pm_sys_audit_log")
public class SysAuditLog {
    @TableId
    private String auditId;
    private String userId;
    private String module;
    private String operation;
    private String ipAddress;
    private String requestUri;
    private String requestBody;
    private String responseCode;
    private String beforeValue;
    private String afterValue;
    private LocalDateTime createTime;
}
