package com.bank.updg.updg_system.service;

import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.baomidou.mybatisplus.extension.service.IService;
import com.bank.updg.updg_system.model.entity.ReviewMeeting;
import com.bank.updg.updg_system.model.entity.ReviewOpinion;

import java.util.Map;

public interface ReviewMeetingService extends IService<ReviewMeeting> {

    /**
     * Create a new review meeting
     */
    ReviewMeeting createMeeting(ReviewMeeting meeting);

    /**
     * Update an existing meeting
     */
    void updateMeeting(String meetingId, ReviewMeeting meeting);

    /**
     * Get meeting detail by ID
     */
    ReviewMeeting getMeeting(String meetingId);

    /**
     * List meetings with filters
     */
    Page<ReviewMeeting> listMeetings(String type, String status, int page, int size);

    /**
     * Submit a review opinion
     */
    ReviewOpinion submitOpinion(String meetingId, String reviewer, String opinion, String vote);

    /**
     * Close a meeting with decision and resolution
     */
    void closeMeeting(String meetingId, String decision, String resolution);

    /**
     * Get meeting statistics
     */
    Map<String, Object> getMeetingStats(String meetingId);
}
