package com.bank.updg.updg_system.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.bank.updg.common.exception.BusinessException;
import com.bank.updg.common.model.enums.ErrorCodeEnum;
import com.bank.updg.updg_system.mapper.ReviewMeetingMapper;
import com.bank.updg.updg_system.mapper.ReviewOpinionMapper;
import com.bank.updg.updg_system.model.entity.ReviewMeeting;
import com.bank.updg.updg_system.model.entity.ReviewOpinion;
import com.bank.updg.updg_system.service.ReviewMeetingService;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
import java.util.LinkedHashMap;
import java.util.Map;
import java.util.UUID;

@Service
@RequiredArgsConstructor
public class ReviewMeetingServiceImpl extends com.baomidou.mybatisplus.extension.service.impl.ServiceImpl<ReviewMeetingMapper, ReviewMeeting> implements ReviewMeetingService {

    private final ReviewOpinionMapper opinionMapper;

    @Override
    public ReviewMeeting createMeeting(ReviewMeeting meeting) {
        if (meeting.getMeetingId() == null) {
            meeting.setMeetingId(UUID.randomUUID().toString().replace("-", ""));
        }
        if (meeting.getStatus() == null) {
            meeting.setStatus("SCHEDULED");
        }
        meeting.setCreateTime(LocalDateTime.now());
        meeting.setUpdateTime(LocalDateTime.now());
        save(meeting);
        return meeting;
    }

    @Override
    public void updateMeeting(String meetingId, ReviewMeeting meeting) {
        ReviewMeeting existing = getById(meetingId);
        if (existing == null) {
            throw new BusinessException(ErrorCodeEnum.NOT_FOUND, "Meeting not found: " + meetingId);
        }
        meeting.setMeetingId(meetingId);
        meeting.setUpdateTime(LocalDateTime.now());
        updateById(meeting);
    }

    @Override
    public ReviewMeeting getMeeting(String meetingId) {
        ReviewMeeting meeting = getById(meetingId);
        if (meeting == null) {
            throw new BusinessException(ErrorCodeEnum.NOT_FOUND, "Meeting not found: " + meetingId);
        }
        return meeting;
    }

    @Override
    public Page<ReviewMeeting> listMeetings(String type, String status, int page, int size) {
        Page<ReviewMeeting> pageObj = new Page<>(page, size);
        LambdaQueryWrapper<ReviewMeeting> wrapper = new LambdaQueryWrapper<>();
        if (type != null && !type.isBlank()) {
            wrapper.eq(ReviewMeeting::getMeetingType, type);
        }
        if (status != null && !status.isBlank()) {
            wrapper.eq(ReviewMeeting::getStatus, status);
        }
        wrapper.orderByDesc(ReviewMeeting::getCreateTime);
        return page(pageObj, wrapper);
    }

    @Override
    public ReviewOpinion submitOpinion(String meetingId, String reviewer, String opinion, String vote) {
        ReviewMeeting meeting = getById(meetingId);
        if (meeting == null) {
            throw new BusinessException(ErrorCodeEnum.NOT_FOUND, "Meeting not found: " + meetingId);
        }
        ReviewOpinion reviewOpinion = ReviewOpinion.builder()
                .opinionId(UUID.randomUUID().toString().replace("-", ""))
                .meetingId(meetingId)
                .reviewer(reviewer)
                .opinion(opinion)
                .vote(vote)
                .createTime(LocalDateTime.now())
                .build();
        opinionMapper.insert(reviewOpinion);
        return reviewOpinion;
    }

    @Override
    public void closeMeeting(String meetingId, String decision, String resolution) {
        ReviewMeeting meeting = getById(meetingId);
        if (meeting == null) {
            throw new BusinessException(ErrorCodeEnum.NOT_FOUND, "Meeting not found: " + meetingId);
        }
        meeting.setDecision(decision);
        meeting.setResolution(resolution);
        meeting.setStatus("CLOSED");
        meeting.setUpdateTime(LocalDateTime.now());
        updateById(meeting);
    }

    @Override
    public Map<String, Object> getMeetingStats(String meetingId) {
        ReviewMeeting meeting = getById(meetingId);
        if (meeting == null) {
            throw new BusinessException(ErrorCodeEnum.NOT_FOUND, "Meeting not found: " + meetingId);
        }

        // Count opinions
        long opinionCount = opinionMapper.selectCount(
                new LambdaQueryWrapper<ReviewOpinion>()
                        .eq(ReviewOpinion::getMeetingId, meetingId));

        // Count by vote type
        long approveCount = opinionMapper.selectCount(
                new LambdaQueryWrapper<ReviewOpinion>()
                        .eq(ReviewOpinion::getMeetingId, meetingId)
                        .eq(ReviewOpinion::getVote, "APPROVE"));
        long rejectCount = opinionMapper.selectCount(
                new LambdaQueryWrapper<ReviewOpinion>()
                        .eq(ReviewOpinion::getMeetingId, meetingId)
                        .eq(ReviewOpinion::getVote, "REJECT"));
        long abstainCount = opinionMapper.selectCount(
                new LambdaQueryWrapper<ReviewOpinion>()
                        .eq(ReviewOpinion::getMeetingId, meetingId)
                        .eq(ReviewOpinion::getVote, "ABSTAIN"));

        Map<String, Object> stats = new LinkedHashMap<>();
        stats.put("meetingId", meetingId);
        stats.put("title", meeting.getTitle());
        stats.put("status", meeting.getStatus());
        stats.put("totalOpinions", opinionCount);
        stats.put("approveCount", approveCount);
        stats.put("rejectCount", rejectCount);
        stats.put("abstainCount", abstainCount);
        stats.put("decision", meeting.getDecision());
        return stats;
    }
}
