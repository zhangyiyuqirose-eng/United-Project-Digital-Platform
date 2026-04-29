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
@TableName("pm_build_record")
public class BuildRecord {

    @TableId
    private String id;

    private String projectId;

    private String repoId;

    private String buildNumber;

    private String status; // SUCCESS, FAILED, RUNNING

    private Long duration;

    private String triggeredBy;

    private String commitHash;

    private LocalDateTime createdAt;
}
