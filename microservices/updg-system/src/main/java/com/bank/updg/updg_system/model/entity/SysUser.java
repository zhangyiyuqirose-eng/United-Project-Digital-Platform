package com.bank.updg.updg_system.model.entity;

import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;

import java.time.LocalDateTime;

/**
 * 用户实体
 */
@Data
@TableName("pm_sys_user")
public class SysUser {
    @TableId
    private String userId;
    private String username;
    private String password;
    private String name;
    private String deptId;
    private String email;
    private String phone;
    private Integer status;
    private LocalDateTime createTime;
    private LocalDateTime updateTime;
}
