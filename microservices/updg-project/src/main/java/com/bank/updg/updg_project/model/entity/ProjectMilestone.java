package com.bank.updg.updg_project.model.entity;

import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;

import java.time.LocalDateTime;

@Data
@TableName("pm_project_milestone")
public class ProjectMilestone {
    @TableId
    private String milestoneId;
    private String projectId;
    private String milestoneName;
    private LocalDateTime planTime;
    private LocalDateTime actualTime;
    private String status;
    private Integer sort;
    private LocalDateTime createTime;
}
