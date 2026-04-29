package com.bank.updg.updg_system.controller;

import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.bank.updg.common.model.ApiResponse;
import com.bank.updg.updg_system.model.entity.ReviewMeeting;
import com.bank.updg.updg_system.model.entity.ReviewOpinion;
import com.bank.updg.updg_system.service.ReviewMeetingService;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

import java.util.Map;

@RestController
@RequestMapping("/api/system/review-meeting")
@RequiredArgsConstructor
public class ReviewMeetingController {

    private final ReviewMeetingService reviewMeetingService;

    /**
     * Create a new review meeting
     */
    @PostMapping
    public ApiResponse<ReviewMeeting> create(@RequestBody ReviewMeeting meeting) {
        return ApiResponse.success(reviewMeetingService.createMeeting(meeting));
    }

    /**
     * Update an existing meeting
     */
    @PutMapping("/{id}")
    public ApiResponse<Void> update(@PathVariable String id, @RequestBody ReviewMeeting meeting) {
        reviewMeetingService.updateMeeting(id, meeting);
        return ApiResponse.success();
    }

    /**
     * Get meeting detail
     */
    @GetMapping("/{id}")
    public ApiResponse<ReviewMeeting> getById(@PathVariable String id) {
        return ApiResponse.success(reviewMeetingService.getMeeting(id));
    }

    /**
     * List meetings with filters
     */
    @GetMapping("/list")
    public ApiResponse<Page<ReviewMeeting>> list(
            @RequestParam(required = false) String type,
            @RequestParam(required = false) String status,
            @RequestParam(defaultValue = "1") int page,
            @RequestParam(defaultValue = "10") int size) {
        return ApiResponse.success(reviewMeetingService.listMeetings(type, status, page, size));
    }

    /**
     * Submit a review opinion
     */
    @PostMapping("/{id}/opinion")
    public ApiResponse<ReviewOpinion> submitOpinion(
            @PathVariable String id,
            @RequestBody Map<String, String> body) {
        String reviewer = body.get("reviewer");
        String opinion = body.get("opinion");
        String vote = body.get("vote");
        return ApiResponse.success(reviewMeetingService.submitOpinion(id, reviewer, opinion, vote));
    }

    /**
     * Close meeting with decision
     */
    @PutMapping("/{id}/close")
    public ApiResponse<Void> close(
            @PathVariable String id,
            @RequestBody Map<String, String> body) {
        String decision = body.get("decision");
        String resolution = body.get("resolution");
        reviewMeetingService.closeMeeting(id, decision, resolution);
        return ApiResponse.success();
    }

    /**
     * Get meeting statistics
     */
    @GetMapping("/{id}/stats")
    public ApiResponse<Map<String, Object>> stats(@PathVariable String id) {
        return ApiResponse.success(reviewMeetingService.getMeetingStats(id));
    }
}
