package com.bank.updg.updg_project.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.bank.updg.common.exception.BusinessException;
import com.bank.updg.common.model.enums.ErrorCodeEnum;
import com.bank.updg.updg_project.mapper.ProjectTaskMapper;
import com.bank.updg.updg_project.model.entity.ProjectTask;
import com.bank.updg.updg_project.service.TaskService;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.time.LocalDate;
import java.time.LocalDateTime;
import java.util.*;

@Service
@RequiredArgsConstructor
public class TaskServiceImpl implements TaskService {

    private final ProjectTaskMapper taskMapper;

    @Override
    public ProjectTask createTask(ProjectTask task) {
        task.setTaskId(UUID.randomUUID().toString().replace("-", ""));
        task.setStatus("NOT_STARTED");
        task.setCreateTime(LocalDateTime.now());
        task.setUpdateTime(LocalDateTime.now());
        taskMapper.insert(task);
        return task;
    }

    @Override
    public void updateTask(String taskId, ProjectTask task) {
        task.setTaskId(taskId);
        task.setUpdateTime(LocalDateTime.now());
        taskMapper.updateById(task);
    }

    @Override
    public ProjectTask getTask(String taskId) {
        ProjectTask task = taskMapper.selectById(taskId);
        if (task == null) {
            throw new BusinessException(ErrorCodeEnum.NOT_FOUND, "Task not found: " + taskId);
        }
        return task;
    }

    @Override
    public Page<ProjectTask> listByProject(String projectId, String status, String assignee, int page, int size) {
        Page<ProjectTask> pageObj = new Page<>(page, size);
        LambdaQueryWrapper<ProjectTask> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(ProjectTask::getProjectId, projectId);
        if (status != null && !status.isEmpty()) {
            wrapper.eq(ProjectTask::getStatus, status);
        }
        if (assignee != null && !assignee.isEmpty()) {
            wrapper.eq(ProjectTask::getAssignee, assignee);
        }
        wrapper.orderByDesc(ProjectTask::getCreateTime);
        return taskMapper.selectPage(pageObj, wrapper);
    }

    @Override
    public List<ProjectTask> getTaskTree(String projectId) {
        LambdaQueryWrapper<ProjectTask> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(ProjectTask::getProjectId, projectId)
               .orderByAsc(ProjectTask::getWbsNode);
        return taskMapper.selectList(wrapper);
    }

    @Override
    public void updateProgress(String taskId, int progress) {
        if (progress < 0 || progress > 100) {
            throw new BusinessException(ErrorCodeEnum.PARAM_ERROR, "progress must be between 0 and 100");
        }
        ProjectTask task = getTask(taskId);
        task.setProgress(progress);
        task.setUpdateTime(LocalDateTime.now());
        if (progress == 100) {
            task.setStatus("DONE");
            task.setActualEndDate(LocalDate.now());
        } else if (progress > 0 && "NOT_STARTED".equals(task.getStatus())) {
            task.setStatus("IN_PROGRESS");
            task.setActualStartDate(LocalDate.now());
        }
        taskMapper.updateById(task);
    }

    @Override
    public void blockTask(String taskId, String reason) {
        ProjectTask task = getTask(taskId);
        task.setStatus("BLOCKED");
        task.setDescription(task.getDescription() + "\n[Blocked: " + reason + "]");
        task.setUpdateTime(LocalDateTime.now());
        taskMapper.updateById(task);
    }

    @Override
    public void completeTask(String taskId) {
        updateProgress(taskId, 100);
    }

    @Override
    public List<ProjectTask> getOverdueTasks(String projectId) {
        LambdaQueryWrapper<ProjectTask> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(ProjectTask::getProjectId, projectId)
               .in(ProjectTask::getStatus, "NOT_STARTED", "IN_PROGRESS")
               .lt(ProjectTask::getEndDate, LocalDate.now());
        return taskMapper.selectList(wrapper);
    }

    @Override
    public void deleteTask(String taskId) {
        // Check no children
        LambdaQueryWrapper<ProjectTask> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(ProjectTask::getParentTaskId, taskId);
        long children = taskMapper.selectCount(wrapper);
        if (children > 0) {
            throw new BusinessException(ErrorCodeEnum.PARAM_ERROR, "Cannot delete task with children");
        }
        taskMapper.deleteById(taskId);
    }

    @Override
    public Map<String, List<String>> getDependencies(String projectId) {
        LambdaQueryWrapper<ProjectTask> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(ProjectTask::getProjectId, projectId);
        List<ProjectTask> tasks = taskMapper.selectList(wrapper);

        Map<String, List<String>> deps = new LinkedHashMap<>();
        for (ProjectTask task : tasks) {
            List<String> predecessors = new ArrayList<>();
            if (task.getPredecessorIds() != null && !task.getPredecessorIds().isEmpty()) {
                for (String pred : task.getPredecessorIds().split(",")) {
                    String trimmed = pred.trim();
                    if (!trimmed.isEmpty()) {
                        predecessors.add(trimmed);
                    }
                }
            }
            deps.put(task.getTaskId(), predecessors);
        }
        return deps;
    }

    @Override
    public List<String> getDownstreamTasks(String taskId) {
        // Get the project of the task
        ProjectTask task = getTask(taskId);
        String projectId = task.getProjectId();

        // Build adjacency: successor -> list of successors
        LambdaQueryWrapper<ProjectTask> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(ProjectTask::getProjectId, projectId);
        List<ProjectTask> allTasks = taskMapper.selectList(wrapper);

        Map<String, List<String>> successors = new HashMap<>();
        for (ProjectTask t : allTasks) {
            if (t.getPredecessorIds() != null && !t.getPredecessorIds().isEmpty()) {
                for (String pred : t.getPredecessorIds().split(",")) {
                    String trimmed = pred.trim();
                    if (!trimmed.isEmpty()) {
                        successors.computeIfAbsent(trimmed, k -> new ArrayList<>()).add(t.getTaskId());
                    }
                }
            }
        }

        // BFS from taskId to find all downstream tasks
        List<String> downstream = new ArrayList<>();
        Set<String> visited = new HashSet<>();
        Queue<String> queue = new LinkedList<>();
        queue.offer(taskId);
        visited.add(taskId);

        while (!queue.isEmpty()) {
            String current = queue.poll();
            for (String succ : successors.getOrDefault(current, Collections.emptyList())) {
                if (visited.add(succ)) {
                    downstream.add(succ);
                    queue.offer(succ);
                }
            }
        }

        return downstream;
    }
}
