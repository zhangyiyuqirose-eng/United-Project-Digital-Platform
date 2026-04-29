package com.bank.updg.updg_notify.model.entity;

import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;

/**
 * F-1409: Notification template entity.
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
@TableName("pm_notify_template")
public class NotifyTemplate {

    @TableId
    private String templateId;

    private String name;

    /** WECHAT, EMAIL, SMS */
    private String channel;

    private String subject;

    private String content;

    /** JSON array of variable names */
    private String variables;

    /** Y, N */
    private String isActive;

    private String createdBy;

    private LocalDateTime createTime;

    private LocalDateTime updateTime;
}