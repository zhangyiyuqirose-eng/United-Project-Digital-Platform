package com.bank.updg.updg_project.service;

import com.baomidou.mybatisplus.extension.service.IService;
import com.bank.updg.updg_project.model.entity.CodeRepo;

import java.util.List;

public interface CodeRepoService extends IService<CodeRepo> {

    CodeRepo registerRepo(CodeRepo repo);

    List<CodeRepo> getByProjectId(String projectId);

    void syncRepo(String repoId);
}
