package com.bank.updg.updg_knowledge.model.entity;

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
@TableName("pm_knowledge_doc")
public class KnowledgeDoc {

    @TableId
    private String docId;

    private String title;

    private String category;

    private String templateType;

    private String filePath;

    private String version;

    private String createdBy;

    private Integer versionNum;

    private LocalDateTime createTime;

    private LocalDateTime updateTime;
}
