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
@TableName("pm_code_repo")
public class CodeRepo {

    @TableId
    private String id;

    private String projectId;

    private String repoUrl;

    private String branch;

    private String type; // GIT, SVN

    private LocalDateTime lastSyncAt;

    private LocalDateTime createdAt;
}
