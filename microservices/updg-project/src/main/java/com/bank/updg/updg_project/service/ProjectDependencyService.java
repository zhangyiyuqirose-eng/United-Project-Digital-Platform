package com.bank.updg.updg_project.service;

import com.baomidou.mybatisplus.extension.service.IService;
import com.bank.updg.updg_project.model.entity.ProjectDependency;

import java.util.List;

public interface ProjectDependencyService extends IService<ProjectDependency> {

    /** Create a cross-project dependency. */
    ProjectDependency createDependency(ProjectDependency dependency);

    /** List dependencies for a project (both source and target). */
    List<ProjectDependency> getByProjectId(String projectId);

    /** Remove a dependency. */
    void removeDependency(String id);
}
