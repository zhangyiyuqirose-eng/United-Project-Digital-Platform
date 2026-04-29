package com.bank.updg.updg_system.model.entity;

import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;

/**
 * 部门实体
 */
@Data
@TableName("pm_sys_dept")
public class SysDept {
    @TableId
    private String deptId;
    private String deptName;
    private String parentId;
    private Integer sort;
    private Integer status;
}
