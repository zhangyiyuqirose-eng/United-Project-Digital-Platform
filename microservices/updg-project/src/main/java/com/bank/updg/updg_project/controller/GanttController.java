package com.bank.updg.updg_project.controller;

import com.bank.updg.common.model.ApiResponse;
import com.bank.updg.updg_project.mapper.ProjectMilestoneMapper;
import com.bank.updg.updg_project.mapper.ProjectTaskMapper;
import com.bank.updg.updg_project.model.entity.ProjectMilestone;
import com.bank.updg.updg_project.model.entity.ProjectTask;
import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

import java.time.format.DateTimeFormatter;
import java.util.*;
import java.util.stream.Collectors;

/**
 * Gantt chart data API (F-106/301).
 * Returns project milestones and tasks in DHTMLX Gantt format.
 */
@RestController
@RequestMapping("/api/project/gantt")
@RequiredArgsConstructor
public class GanttController {

    private static final DateTimeFormatter DATE_FMT = DateTimeFormatter.ofPattern("yyyy-MM-dd");

    private final ProjectMilestoneMapper milestoneMapper;
    private final ProjectTaskMapper taskMapper;

    @GetMapping("/{projectId}")
    public ApiResponse<Map<String, Object>> getGanttData(@PathVariable String projectId) {
        // Fetch milestones for this project
        List<ProjectMilestone> milestones = milestoneMapper.selectList(
                new LambdaQueryWrapper<ProjectMilestone>()
                        .eq(ProjectMilestone::getProjectId, projectId)
                        .orderByAsc(ProjectMilestone::getSort));

        // Fetch tasks for this project
        List<ProjectTask> tasks = taskMapper.selectList(
                new LambdaQueryWrapper<ProjectTask>()
                        .eq(ProjectTask::getProjectId, projectId));

        List<Map<String, Object>> data = new ArrayList<>();

        // Add milestones as parent nodes
        for (ProjectMilestone m : milestones) {
            Map<String, Object> node = new LinkedHashMap<>();
            node.put("id", "ms-" + m.getMilestoneId());
            node.put("text", m.getMilestoneName());
            node.put("start_date", m.getPlanTime() != null
                    ? m.getPlanTime().format(DATE_FMT) : "");
            node.put("duration", 1);
            node.put("parent", 0);
            node.put("progress", m.getStatus() != null && "COMPLETED".equals(m.getStatus()) ? 1.0 : 0.0);
            node.put("type", "project");
            data.add(node);

            // Add tasks belonging to this milestone
            List<ProjectTask> milestoneTasks = tasks.stream()
                    .filter(t -> m.getMilestoneName() != null
                            && t.getWbsNode() != null
                            && t.getWbsNode().contains(m.getMilestoneName()))
                    .collect(Collectors.toList());

            for (ProjectTask t : milestoneTasks) {
                Map<String, Object> taskNode = new LinkedHashMap<>();
                taskNode.put("id", "t-" + t.getTaskId());
                taskNode.put("text", t.getTaskName());
                taskNode.put("start_date", t.getStartDate() != null
                        ? t.getStartDate().format(DATE_FMT) : "");
                taskNode.put("duration", calcDuration(t.getStartDate(), t.getEndDate()));
                taskNode.put("parent", "ms-" + m.getMilestoneId());
                taskNode.put("progress", t.getProgress() != null
                        ? t.getProgress() / 100.0 : 0.0);
                data.add(taskNode);
            }
        }

        // Add tasks not associated with any milestone
        Set<String> assignedTaskIds = tasks.stream()
                .filter(t -> t.getWbsNode() != null)
                .map(ProjectTask::getTaskId)
                .collect(Collectors.toSet());

        for (ProjectTask t : tasks) {
            if (assignedTaskIds.contains(t.getTaskId())) continue;
            Map<String, Object> taskNode = new LinkedHashMap<>();
            taskNode.put("id", "t-" + t.getTaskId());
            taskNode.put("text", t.getTaskName());
            taskNode.put("start_date", t.getStartDate() != null
                    ? t.getStartDate().format(DATE_FMT) : "");
            taskNode.put("duration", calcDuration(t.getStartDate(), t.getEndDate()));
            taskNode.put("parent", 0);
            taskNode.put("progress", t.getProgress() != null
                    ? t.getProgress() / 100.0 : 0.0);
            data.add(taskNode);
        }

        // Build dependency links from predecessor IDs
        List<Map<String, Object>> links = new ArrayList<>();
        int linkIdx = 0;
        for (ProjectTask t : tasks) {
            if (t.getPredecessorIds() != null && !t.getPredecessorIds().isEmpty()) {
                String[] preds = t.getPredecessorIds().split(",");
                for (String pred : preds) {
                    String trimmed = pred.trim();
                    if (!trimmed.isEmpty()) {
                        Map<String, Object> link = new LinkedHashMap<>();
                        link.put("id", linkIdx++);
                        link.put("source", "t-" + trimmed);
                        link.put("target", "t-" + t.getTaskId());
                        link.put("type", "0"); // 0 = FS (Finish-to-Start)
                        links.add(link);
                    }
                }
            }
        }

        Map<String, Object> result = new LinkedHashMap<>();
        result.put("data", data);
        result.put("links", links);
        return ApiResponse.success(result);
    }

    private int calcDuration(java.time.LocalDate start, java.time.LocalDate end) {
        if (start == null || end == null) return 1;
        long days = java.time.temporal.ChronoUnit.DAYS.between(start, end);
        return days > 0 ? (int) days : 1;
    }
}
