package com.bank.updg.updg_system.model.entity;

import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;

/**
 * 权限实体
 */
@Data
@TableName("pm_sys_permission")
public class SysPermission {
    @TableId
    private String permissionId;
    private String permissionName;
    private String permissionCode;
    private String type;
    private String parentId;
    private Integer sort;
}
