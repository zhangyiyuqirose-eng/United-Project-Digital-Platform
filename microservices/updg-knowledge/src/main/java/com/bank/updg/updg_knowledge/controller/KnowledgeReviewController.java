package com.bank.updg.updg_knowledge.controller;

import com.bank.updg.common.model.ApiResponse;
import com.bank.updg.updg_knowledge.model.entity.KnowledgeReview;
import com.bank.updg.updg_knowledge.service.KnowledgeReviewService;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

/**
 * F-905: Knowledge review management.
 */
@RestController
@RequestMapping("/api/knowledge/review")
@RequiredArgsConstructor
public class KnowledgeReviewController {

    private final KnowledgeReviewService reviewService;

    @PostMapping
    public ApiResponse<KnowledgeReview> submit(@RequestBody KnowledgeReview review) {
        return ApiResponse.success(reviewService.submitReview(review));
    }

    @GetMapping("/doc/{docId}")
    public ApiResponse<List<KnowledgeReview>> getByDoc(@PathVariable String docId) {
        return ApiResponse.success(reviewService.getByDocId(docId));
    }

    @GetMapping("/pending/{reviewerId}")
    public ApiResponse<List<KnowledgeReview>> getPending(@PathVariable String reviewerId) {
        return ApiResponse.success(reviewService.getPendingByReviewer(reviewerId));
    }

    @PostMapping("/{reviewId}/approve")
    public ApiResponse<Void> approve(@PathVariable String reviewId,
                                     @RequestBody Map<String, String> body) {
        reviewService.approveReview(reviewId, body.get("comment"));
        return ApiResponse.success();
    }

    @PostMapping("/{reviewId}/reject")
    public ApiResponse<Void> reject(@PathVariable String reviewId,
                                    @RequestBody Map<String, String> body) {
        reviewService.rejectReview(reviewId, body.get("comment"));
        return ApiResponse.success();
    }
}
