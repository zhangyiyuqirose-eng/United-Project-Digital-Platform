package com.bank.updg.updg_system.model.entity;

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
@TableName("pm_review_meeting")
public class ReviewMeeting {

    @TableId
    private String meetingId;

    private String meetingType;

    private String title;

    private String description;

    private LocalDateTime meetingDate;

    private String startTime;

    private String endTime;

    private String location;

    private String organizer;

    private String attendees;

    private String agenda;

    private String materials;

    private String status;

    private String decision;

    private String resolution;

    private String meetingNotes;

    private LocalDateTime createTime;

    private LocalDateTime updateTime;
}
