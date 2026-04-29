package com.bank.updg.updg_notify.model.entity;

import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;

/**
 * User notification preference entity.
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
@TableName("pm_notify_preference")
public class NotifyPreference {

    @TableId
    private String prefId;

    private String userId;

    /** WECHAT, EMAIL, SMS */
    private String channel;

    /** Whether this channel is enabled (1=enabled, 0=disabled) */
    private Integer enabled;

    /** Comma-separated business types to receive */
    private String bizTypes;

    /** Quiet period start (HH:mm) */
    private String quietStart;

    /** Quiet period end (HH:mm) */
    private String quietEnd;

    private LocalDateTime createTime;

    private LocalDateTime updateTime;
}
