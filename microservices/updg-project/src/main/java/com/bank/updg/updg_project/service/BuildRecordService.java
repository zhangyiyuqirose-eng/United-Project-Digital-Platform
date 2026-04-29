package com.bank.updg.updg_project.service;

import com.baomidou.mybatisplus.extension.service.IService;
import com.bank.updg.updg_project.model.entity.BuildRecord;

import java.util.List;

public interface BuildRecordService extends IService<BuildRecord> {

    BuildRecord recordBuild(BuildRecord record);

    List<BuildRecord> getByProjectId(String projectId);
}
