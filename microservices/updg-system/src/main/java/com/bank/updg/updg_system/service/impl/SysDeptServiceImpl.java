package com.bank.updg.updg_system.service.impl;

import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import com.bank.updg.updg_system.mapper.SysDeptMapper;
import com.bank.updg.updg_system.model.entity.SysDept;
import com.bank.updg.updg_system.service.SysDeptService;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
@RequiredArgsConstructor
public class SysDeptServiceImpl extends ServiceImpl<SysDeptMapper, SysDept> implements SysDeptService {

    @Override
    public void createDept(SysDept dept) {
        save(dept);
    }

    @Override
    public void updateDept(SysDept dept) {
        updateById(dept);
    }

    @Override
    public void deleteDept(String deptId) {
        removeById(deptId);
    }

    @Override
    public List<SysDept> listTree() {
        return list();
    }
}
