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
@TableName("pm_meeting")
public class Meeting {

    @TableId
    private String id;

    private String title;

    private String type; // PROJECT, REVIEW, STATUS, AD_HOC

    private String projectId;

    private String organizer;

    private String attendees; // JSON

    private LocalDateTime scheduledAt;

    private String location;

    private String agenda;

    private String status; // SCHEDULED, COMPLETED, CANCELLED

    private String minutes;

    private LocalDateTime createdAt;
}
