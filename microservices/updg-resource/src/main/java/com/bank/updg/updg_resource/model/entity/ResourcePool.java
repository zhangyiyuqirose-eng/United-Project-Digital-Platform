package com.bank.updg.updg_resource.model.entity;

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
@TableName("pm_resource_pool")
public class ResourcePool {

    @TableId
    private String poolId;

    private String poolName;

    private String managerId;

    private String description;

    private LocalDateTime createTime;
}
