package com.bank.updg.updg_auth.model.entity;

import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;

import java.time.LocalDateTime;

@Data
@TableName("pm_sys_user")
public class User {
    @TableId
    private String userId;
    private String username;
    private String password;
    private String name;
    private String deptId;
    private String email;
    private String phone;
    private Integer status;
    private LocalDateTime passwordChangedAt;
    private LocalDateTime createTime;
    private LocalDateTime updateTime;
}
