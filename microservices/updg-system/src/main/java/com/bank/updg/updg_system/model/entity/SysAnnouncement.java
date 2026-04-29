package com.bank.updg.updg_system.model.entity;

import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;

/**
 * System announcement management (F-1413).
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
@TableName("pm_sys_announcement")
public class SysAnnouncement {

    @TableId
    private String announcementId;

    private String title;

    private String content;

    /** NOTICE, URGENT, SYSTEM */
    private String type;

    /** LOW, MEDIUM, HIGH */
    private String priority;

    private String publisher;

    private LocalDateTime publishTime;

    private LocalDateTime expiryTime;

    /** DRAFT, PUBLISHED, EXPIRED */
    private String status;

    /** JSON array of target department IDs */
    private String targetDept;

    /** JSON array of target role IDs */
    private String targetRoles;

    private LocalDateTime createTime;
}
