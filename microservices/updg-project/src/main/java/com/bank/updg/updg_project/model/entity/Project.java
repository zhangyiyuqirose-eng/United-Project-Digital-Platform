package com.bank.updg.updg_project.model.entity;

import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;

import java.math.BigDecimal;
import java.time.LocalDate;
import java.time.LocalDateTime;

@Data
@TableName("pm_project")
public class Project {
    @TableId
    private String projectId;
    private String projectCode;
    private String projectName;
    private String projectType;
    private String status;
    private String managerId;
    private String managerName;
    private String departmentId;
    private String departmentName;
    private LocalDate startDate;
    private LocalDate endDate;
    private BigDecimal budget;
    private String customer;
    private String description;
    private Integer progress;
    private String wbsJson;
    private String milestoneJson;
    private BigDecimal evmPv;
    private BigDecimal evmEv;
    private BigDecimal evmAc;
    private BigDecimal evmCpi;
    private BigDecimal evmSpi;
    /** Computed health score 0-100 (F-113) */
    private BigDecimal healthScore;
    private LocalDateTime initTime;
    private LocalDateTime startTime;
    private LocalDateTime endTime;
    private LocalDateTime actualEndTime;
    private String createUser;
    private LocalDateTime createTime;
    private LocalDateTime updateTime;
}
