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
@TableName("pm_review_opinion")
public class ReviewOpinion {

    @TableId
    private String opinionId;

    private String meetingId;

    private String reviewer;

    private String opinion;

    private String vote;

    private String attachment;

    private LocalDateTime createTime;
}
