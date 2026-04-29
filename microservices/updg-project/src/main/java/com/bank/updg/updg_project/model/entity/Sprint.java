package com.bank.updg.updg_project.model.entity;

import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.math.BigDecimal;
import java.time.LocalDate;
import java.time.LocalDateTime;

/**
 * Sprint management (F-309).
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
@TableName("pm_sprint")
public class Sprint {

    @TableId
    private String sprintId;

    private String projectId;

    private String name;

    private String goal;

    private LocalDate startDate;

    private LocalDate endDate;

    /** PLANNED, ACTIVE, COMPLETED, CANCELLED */
    private String status;

    /** Story points completed in this sprint */
    private BigDecimal velocity;

    private LocalDateTime createdAt;

    private LocalDateTime updatedAt;
}
