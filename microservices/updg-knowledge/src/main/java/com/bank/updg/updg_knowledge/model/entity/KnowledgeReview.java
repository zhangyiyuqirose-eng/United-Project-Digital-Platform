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
@TableName("pm_knowledge_review")
public class KnowledgeReview {

    @TableId
    private String id;

    private String docId;

    private String reviewerId;

    private String status; // PENDING, APPROVED, REJECTED

    private String comment;

    private LocalDateTime reviewedAt;
}
