package com.bank.updg.updg_system.model.entity;

import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;

/**
 * 字典实体
 */
@Data
@TableName("pm_sys_dict")
public class SysDict {
    @TableId
    private String dictId;
    private String dictName;
    private String dictCode;
}
