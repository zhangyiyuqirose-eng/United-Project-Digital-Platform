package com.bank.updg.updg_project.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import com.bank.updg.updg_project.mapper.BuildRecordMapper;
import com.bank.updg.updg_project.model.entity.BuildRecord;
import com.bank.updg.updg_project.service.BuildRecordService;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
import java.util.List;
import java.util.UUID;

@Service
public class BuildRecordServiceImpl extends ServiceImpl<BuildRecordMapper, BuildRecord>
        implements BuildRecordService {

    @Override
    public BuildRecord recordBuild(BuildRecord record) {
        record.setId(UUID.randomUUID().toString().replace("-", ""));
        record.setCreatedAt(LocalDateTime.now());
        save(record);
        return record;
    }

    @Override
    public List<BuildRecord> getByProjectId(String projectId) {
        LambdaQueryWrapper<BuildRecord> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(BuildRecord::getProjectId, projectId);
        return list(wrapper);
    }
}
