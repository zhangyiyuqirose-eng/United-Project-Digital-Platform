package com.bank.updg.updg_project.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.bank.updg.common.exception.BusinessException;
import com.bank.updg.common.model.enums.ErrorCodeEnum;
import com.bank.updg.updg_project.mapper.SprintMapper;
import com.bank.updg.updg_project.model.entity.Sprint;
import com.bank.updg.updg_project.service.SprintService;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.List;
import java.util.UUID;

@Service
@RequiredArgsConstructor
public class SprintServiceImpl implements SprintService {

    private final SprintMapper sprintMapper;

    @Override
    public Sprint createSprint(Sprint sprint) {
        sprint.setSprintId(UUID.randomUUID().toString().replace("-", ""));
        sprint.setStatus("PLANNED");
        sprint.setCreatedAt(LocalDateTime.now());
        sprint.setUpdatedAt(LocalDateTime.now());
        sprintMapper.insert(sprint);
        return sprint;
    }

    @Override
    public void updateSprint(String sprintId, Sprint data) {
        Sprint existing = sprintMapper.selectById(sprintId);
        if (existing == null) {
            throw new BusinessException(ErrorCodeEnum.PARAM_ERROR, "Sprint not found: " + sprintId);
        }
        if (data.getName() != null) existing.setName(data.getName());
        if (data.getGoal() != null) existing.setGoal(data.getGoal());
        if (data.getStartDate() != null) existing.setStartDate(data.getStartDate());
        if (data.getEndDate() != null) existing.setEndDate(data.getEndDate());
        existing.setUpdatedAt(LocalDateTime.now());
        sprintMapper.updateById(existing);
    }

    @Override
    public Sprint getSprint(String sprintId) {
        Sprint sprint = sprintMapper.selectById(sprintId);
        if (sprint == null) {
            throw new BusinessException(ErrorCodeEnum.PARAM_ERROR, "Sprint not found: " + sprintId);
        }
        return sprint;
    }

    @Override
    public List<Sprint> listByProject(String projectId) {
        LambdaQueryWrapper<Sprint> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(Sprint::getProjectId, projectId)
                .orderByAsc(Sprint::getStartDate);
        return sprintMapper.selectList(wrapper);
    }

    @Override
    public Page<Sprint> pageByProject(String projectId, int page, int size) {
        Page<Sprint> pageObj = new Page<>(page, size);
        LambdaQueryWrapper<Sprint> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(Sprint::getProjectId, projectId)
                .orderByAsc(Sprint::getStartDate);
        return sprintMapper.selectPage(pageObj, wrapper);
    }

    @Override
    public void completeSprint(String sprintId, BigDecimal velocity) {
        Sprint sprint = getSprint(sprintId);
        sprint.setStatus("COMPLETED");
        sprint.setVelocity(velocity);
        sprint.setUpdatedAt(LocalDateTime.now());
        sprintMapper.updateById(sprint);
    }

    @Override
    public void cancelSprint(String sprintId) {
        Sprint sprint = getSprint(sprintId);
        sprint.setStatus("CANCELLED");
        sprint.setUpdatedAt(LocalDateTime.now());
        sprintMapper.updateById(sprint);
    }

    @Override
    public Sprint getActiveSprint(String projectId) {
        LambdaQueryWrapper<Sprint> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(Sprint::getProjectId, projectId)
                .eq(Sprint::getStatus, "ACTIVE")
                .orderByDesc(Sprint::getStartDate)
                .last("LIMIT 1");
        return sprintMapper.selectOne(wrapper);
    }
}
