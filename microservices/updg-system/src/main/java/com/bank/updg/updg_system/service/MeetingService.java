package com.bank.updg.updg_system.service;

import com.baomidou.mybatisplus.extension.service.IService;
import com.bank.updg.updg_system.model.entity.Meeting;

import java.util.List;

public interface MeetingService extends IService<Meeting> {

    Meeting createMeeting(Meeting meeting);

    List<Meeting> getByProjectId(String projectId);

    void completeMeeting(String id, String minutes);

    void cancelMeeting(String id);
}
