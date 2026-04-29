package com.bank.updg.updg_project.model.entity;

import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;

import java.time.LocalDateTime;

@Data
@TableName("pm_project_close")
public class ProjectClose {
    @TableId
    private String closeId;
    private String projectId;
    private LocalDateTime closeTime;
    private String summary;
    private String costSummary;
    private String lessonsLearned;
    private String createUser;
    private LocalDateTime createTime;
}
