package com.bank.updg.updg_project.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import com.bank.updg.updg_project.mapper.ProjectDependencyMapper;
import com.bank.updg.updg_project.model.entity.ProjectDependency;
import com.bank.updg.updg_project.service.ProjectDependencyService;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.List;
import java.util.UUID;

@Service
public class ProjectDependencyServiceImpl
        extends ServiceImpl<ProjectDependencyMapper, ProjectDependency>
        implements ProjectDependencyService {

    @Override
    public ProjectDependency createDependency(ProjectDependency dependency) {
        dependency.setId(UUID.randomUUID().toString().replace("-", ""));
        dependency.setCreatedAt(LocalDateTime.now());
        save(dependency);
        return dependency;
    }

    @Override
    public List<ProjectDependency> getByProjectId(String projectId) {
        LambdaQueryWrapper<ProjectDependency> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(ProjectDependency::getSourceProjectId, projectId)
                .or()
                .eq(ProjectDependency::getTargetProjectId, projectId);
        return list(wrapper);
    }

    @Override
    public void removeDependency(String id) {
        removeById(id);
    }
}
