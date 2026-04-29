package com.bank.updg.updg_project.service;

import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.bank.updg.updg_project.model.entity.ProjectTask;

import java.util.List;
import java.util.Map;

public interface TaskService {

    /** Create a new task. */
    ProjectTask createTask(ProjectTask task);

    /** Update task details. */
    void updateTask(String taskId, ProjectTask task);

    /** Get task by ID. */
    ProjectTask getTask(String taskId);

    /** List tasks by project with optional filters. */
    Page<ProjectTask> listByProject(String projectId, String status, String assignee, int page, int size);

    /** Get task tree (hierarchical) for a project. */
    List<ProjectTask> getTaskTree(String projectId);

    /** Update task progress. */
    void updateProgress(String taskId, int progress);

    /** Block a task. */
    void blockTask(String taskId, String reason);

    /** Complete a task. */
    void completeTask(String taskId);

    /** Get tasks overdue. */
    List<ProjectTask> getOverdueTasks(String projectId);

    /** Delete task (only if no children). */
    void deleteTask(String taskId);

    /**
     * F-308: Returns dependency adjacency list for a project.
     * Map of taskId -> list of predecessor task IDs.
     */
    Map<String, List<String>> getDependencies(String projectId);

    /**
     * F-308: Returns all downstream tasks affected by delaying a task.
     */
    List<String> getDownstreamTasks(String taskId);
}
