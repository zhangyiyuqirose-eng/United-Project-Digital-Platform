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
@TableName("pm_sys_config")
public class SysConfig {

    @TableId
    private Long configId;

    private String configKey;

    private String configValue;

    private String configType;

    private String description;

    private String createdBy;

    private LocalDateTime createTime;

    private LocalDateTime updateTime;
}
