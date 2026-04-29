package com.bank.updg.updg_knowledge.service;

import com.baomidou.mybatisplus.extension.service.IService;
import com.bank.updg.updg_knowledge.model.entity.KnowledgeReview;

import java.util.List;

public interface KnowledgeReviewService extends IService<KnowledgeReview> {

    KnowledgeReview submitReview(KnowledgeReview review);

    List<KnowledgeReview> getByDocId(String docId);

    List<KnowledgeReview> getPendingByReviewer(String reviewerId);

    void approveReview(String reviewId, String comment);

    void rejectReview(String reviewId, String comment);
}
