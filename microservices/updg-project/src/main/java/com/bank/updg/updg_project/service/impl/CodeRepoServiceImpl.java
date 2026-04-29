package com.bank.updg.updg_project.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import com.bank.updg.updg_project.mapper.CodeRepoMapper;
import com.bank.updg.updg_project.model.entity.CodeRepo;
import com.bank.updg.updg_project.service.CodeRepoService;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
import java.util.List;
import java.util.UUID;

@Service
public class CodeRepoServiceImpl extends ServiceImpl<CodeRepoMapper, CodeRepo>
        implements CodeRepoService {

    @Override
    public CodeRepo registerRepo(CodeRepo repo) {
        repo.setId(UUID.randomUUID().toString().replace("-", ""));
        repo.setCreatedAt(LocalDateTime.now());
        save(repo);
        return repo;
    }

    @Override
    public List<CodeRepo> getByProjectId(String projectId) {
        LambdaQueryWrapper<CodeRepo> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(CodeRepo::getProjectId, projectId);
        return list(wrapper);
    }

    @Override
    public void syncRepo(String repoId) {
        CodeRepo repo = getById(repoId);
        if (repo != null) {
            repo.setLastSyncAt(LocalDateTime.now());
            updateById(repo);
        }
    }
}
