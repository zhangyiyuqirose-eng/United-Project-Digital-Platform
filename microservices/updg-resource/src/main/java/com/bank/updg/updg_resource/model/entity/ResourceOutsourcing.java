package com.bank.updg.updg_resource.model.entity;

import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.math.BigDecimal;
import java.time.LocalDateTime;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
@TableName("pm_resource_outsourcing")
public class ResourceOutsourcing {

    @TableId
    private String staffId;

    private String name;

    private String idCard;

    private String skill;

    private String resourcePool;

    private LocalDateTime entryTime;

    private LocalDateTime exitTime;

    private BigDecimal rate;

    private String status;

    private LocalDateTime createTime;

    private LocalDateTime updateTime;
}
