package com.bank.updg.updg_notify.model.entity;

import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;

/**
 * Notification message entity.
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
@TableName("pm_notify_message")
public class NotifyMessage {

    @TableId
    private String messageId;

    private String title;

    private String content;

    /** WECHAT, EMAIL, SMS */
    private String channel;

    private String receiver;

    private String sender;

    /** PENDING, SENT, FAILED, READ */
    private String status;

    /** LOW, NORMAL, HIGH, URGENT */
    private String priority;

    private String bizType;

    private String bizId;

    private LocalDateTime sendTime;

    private LocalDateTime readTime;

    private String errorMsg;

    private LocalDateTime createTime;

    private LocalDateTime updateTime;
}
