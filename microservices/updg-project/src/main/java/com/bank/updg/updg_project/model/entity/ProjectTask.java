package com.bank.updg.updg_project.model.entity;

import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDate;
import java.time.LocalDateTime;

/**
 * Project task (F-307 任务管理).
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
@TableName("pm_project_task")
public class ProjectTask {

    @TableId
    private String taskId;

    private String projectId;

    private String parentTaskId;

    private String taskName;

    private String description;

    /** WBS node this task belongs to */
    private String wbsNode;

    private String assignee;

    /** NOT_STARTED, IN_PROGRESS, BLOCKED, DONE, CANCELLED */
    private String status;

    /** LOW, MEDIUM, HIGH, CRITICAL */
    private String priority;

    private Integer estimatedHours;

    private Integer actualHours;

    private Integer progress;

    private LocalDate startDate;

    private LocalDate endDate;

    private LocalDate actualStartDate;

    private LocalDate actualEndDate;

    /** Comma-separated predecessor task IDs */
    private String predecessorIds;

    private String deliverable;

    private LocalDateTime createTime;

    private LocalDateTime updateTime;
}
