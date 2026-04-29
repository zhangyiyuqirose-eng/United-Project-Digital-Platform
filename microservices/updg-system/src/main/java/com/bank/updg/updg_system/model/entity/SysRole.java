package com.bank.updg.updg_system.model.entity;

import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;

import java.time.LocalDateTime;

/**
 * 角色实体
 */
@Data
@TableName("pm_sys_role")
public class SysRole {
    @TableId
    private String roleId;
    private String roleName;
    private String roleCode;
    private String description;
    private Integer status;
    private LocalDateTime createTime;
    private LocalDateTime updateTime;
}
