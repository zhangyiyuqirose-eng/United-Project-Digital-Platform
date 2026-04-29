package com.bank.updg.updg_system.service;

import com.baomidou.mybatisplus.extension.service.IService;
import com.bank.updg.updg_system.model.entity.SysDept;

import java.util.List;

public interface SysDeptService extends IService<SysDept> {

    void createDept(SysDept dept);

    void updateDept(SysDept dept);

    void deleteDept(String deptId);

    List<SysDept> listTree();
}
