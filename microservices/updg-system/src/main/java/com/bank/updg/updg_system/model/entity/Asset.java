package com.bank.updg.updg_system.model.entity;

import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.math.BigDecimal;
import java.time.LocalDate;
import java.time.LocalDateTime;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
@TableName("pm_asset")
public class Asset {

    @TableId
    private String id;

    private String name;

    private String type; // LAPTOP, MONITOR, OTHER

    private String serialNumber;

    private String assignedTo;

    private String projectId;

    private LocalDate purchaseDate;

    private BigDecimal cost;

    private String status; // AVAILABLE, ASSIGNED, RETURNED, DAMAGED

    private LocalDateTime createdAt;
}
