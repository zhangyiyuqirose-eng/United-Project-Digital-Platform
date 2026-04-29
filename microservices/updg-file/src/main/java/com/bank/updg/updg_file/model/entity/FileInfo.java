package com.bank.updg.updg_file.model.entity;

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
@TableName("pm_file_info")
public class FileInfo {

    @TableId
    private String fileId;

    private String fileName;

    private String originalName;

    private String contentType;

    private Long fileSize;

    private String bucket;

    private String objectKey;

    private String uploadedBy;

    private String projectId;

    private String category;

    private String tags;

    private LocalDateTime createTime;

    private LocalDateTime updateTime;
}
