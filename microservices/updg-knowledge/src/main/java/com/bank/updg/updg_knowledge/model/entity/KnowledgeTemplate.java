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
@TableName("pm_knowledge_template")
public class KnowledgeTemplate {

    @TableId
    private String templateId;

    private String name;

    private String type;

    private String description;

    private String fileUrl;

    private String status;

    private LocalDateTime createTime;
}
