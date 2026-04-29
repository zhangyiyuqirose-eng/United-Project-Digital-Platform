package com.bank.updg.updg_project.model.entity;

import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
@TableName("pm_project_dependency")
public class ProjectDependency {

    @TableId
    private String id;

    private String sourceProjectId;

    private String targetProjectId;

    private String type; // FINISH_TO_START, START_TO_START, FINISH_TO_FINISH, START_TO_FINISH

    private String description;

    private LocalDateTime createdAt;
}
