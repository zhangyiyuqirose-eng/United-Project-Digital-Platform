package com.bank.updg.updg_project.model.entity;

import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;

import java.time.LocalDateTime;

@Data
@TableName("pm_project_change")
public class ProjectChange {
    @TableId
    private String changeId;
    private String projectId;
    private String changeType;
    private String content;
    private String reason;
    private String approveStatus;
    private String createUser;
    private LocalDateTime createTime;
}
