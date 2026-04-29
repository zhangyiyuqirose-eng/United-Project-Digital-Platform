package com.bank.updg.updg_knowledge.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import com.bank.updg.updg_knowledge.mapper.KnowledgeReviewMapper;
import com.bank.updg.updg_knowledge.model.entity.KnowledgeReview;
import com.bank.updg.updg_knowledge.service.KnowledgeReviewService;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
import java.util.List;
import java.util.UUID;

@Service
public class KnowledgeReviewServiceImpl
        extends ServiceImpl<KnowledgeReviewMapper, KnowledgeReview>
        implements KnowledgeReviewService {

    @Override
    public KnowledgeReview submitReview(KnowledgeReview review) {
        review.setId(UUID.randomUUID().toString().replace("-", ""));
        review.setStatus("PENDING");
        save(review);
        return review;
    }

    @Override
    public List<KnowledgeReview> getByDocId(String docId) {
        LambdaQueryWrapper<KnowledgeReview> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(KnowledgeReview::getDocId, docId);
        return list(wrapper);
    }

    @Override
    public List<KnowledgeReview> getPendingByReviewer(String reviewerId) {
        LambdaQueryWrapper<KnowledgeReview> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(KnowledgeReview::getReviewerId, reviewerId)
                .eq(KnowledgeReview::getStatus, "PENDING");
        return list(wrapper);
    }

    @Override
    public void approveReview(String reviewId, String comment) {
        KnowledgeReview review = getById(reviewId);
        if (review != null) {
            review.setStatus("APPROVED");
            review.setComment(comment);
            review.setReviewedAt(LocalDateTime.now());
            updateById(review);
        }
    }

    @Override
    public void rejectReview(String reviewId, String comment) {
        KnowledgeReview review = getById(reviewId);
        if (review != null) {
            review.setStatus("REJECTED");
            review.setComment(comment);
            review.setReviewedAt(LocalDateTime.now());
            updateById(review);
        }
    }
}
