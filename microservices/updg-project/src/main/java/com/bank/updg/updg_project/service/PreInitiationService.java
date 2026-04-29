package com.bank.updg.updg_project.service;

import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.bank.updg.updg_project.model.entity.PreInitiation;

public interface PreInitiationService {

    PreInitiation createPreInitiation(PreInitiation data);

    void submitPreInitiation(String preId);

    void approvePreInitiation(String preId, boolean approved, String comment);

    Page<PreInitiation> listByDept(String deptId, String status, int page, int size);

    PreInitiation getPreInitiation(String preId);
}
