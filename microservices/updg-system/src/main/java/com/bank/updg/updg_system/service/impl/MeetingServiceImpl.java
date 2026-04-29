package com.bank.updg.updg_system.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import com.bank.updg.updg_system.mapper.MeetingMapper;
import com.bank.updg.updg_system.model.entity.Meeting;
import com.bank.updg.updg_system.service.MeetingService;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
import java.util.List;
import java.util.UUID;

@Service
public class MeetingServiceImpl extends ServiceImpl<MeetingMapper, Meeting>
        implements MeetingService {

    @Override
    public Meeting createMeeting(Meeting meeting) {
        meeting.setId(UUID.randomUUID().toString().replace("-", ""));
        meeting.setStatus("SCHEDULED");
        meeting.setCreatedAt(LocalDateTime.now());
        save(meeting);
        return meeting;
    }

    @Override
    public List<Meeting> getByProjectId(String projectId) {
        LambdaQueryWrapper<Meeting> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(Meeting::getProjectId, projectId);
        return list(wrapper);
    }

    @Override
    public void completeMeeting(String id, String minutes) {
        Meeting meeting = getById(id);
        if (meeting != null) {
            meeting.setStatus("COMPLETED");
            meeting.setMinutes(minutes);
            updateById(meeting);
        }
    }

    @Override
    public void cancelMeeting(String id) {
        Meeting meeting = getById(id);
        if (meeting != null) {
            meeting.setStatus("CANCELLED");
            updateById(meeting);
        }
    }
}
