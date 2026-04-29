package com.bank.updg.updg_workflow.model.entity;

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
@TableName("pm_process_config")
public class ProcessDefinition {

    @TableId
    private String id;

    private String processKey;

    private String name;

    private String nodes; // JSON

    private String transitions; // JSON

    private Integer version;

    private LocalDateTime createdAt;

    private LocalDateTime updatedAt;
}
