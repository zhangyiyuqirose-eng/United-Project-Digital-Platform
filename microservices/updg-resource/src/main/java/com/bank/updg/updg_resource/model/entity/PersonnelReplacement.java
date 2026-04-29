package com.bank.updg.updg_resource.model.entity;

import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
@TableName("pm_personnel_replacement")
public class PersonnelReplacement {
    @TableId
    private String replacementId;
    private String projectId;
    private String outgoingStaffId;
    private String incomingStaffId;
    private String reason;
    private String status;
    private String handoverNotes;
    private String requestedBy;
    private String requestedAt;
    private String completedAt;
}
