package com.bank.updg.updg_project.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.bank.updg.updg_project.mapper.ProjectTaskMapper;
import com.bank.updg.updg_project.model.entity.ProjectTask;
import com.bank.updg.updg_project.service.CriticalPathService;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.util.*;

@Service
@RequiredArgsConstructor
public class CriticalPathServiceImpl implements CriticalPathService {

    private final ProjectTaskMapper taskMapper;

    @Override
    public List<String> findCriticalPath(String projectId) {
        // Query all tasks for the project
        LambdaQueryWrapper<ProjectTask> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(ProjectTask::getProjectId, projectId);
        List<ProjectTask> tasks = taskMapper.selectList(wrapper);

        if (tasks.isEmpty()) {
            return Collections.emptyList();
        }

        // Build adjacency list and in-degree map
        Map<String, List<String>> successors = new HashMap<>();
        Map<String, Integer> inDegree = new HashMap<>();
        Map<String, Integer> duration = new HashMap<>();

        for (ProjectTask task : tasks) {
            String id = task.getTaskId();
            successors.putIfAbsent(id, new ArrayList<>());
            inDegree.putIfAbsent(id, 0);
            duration.put(id, task.getEstimatedHours() != null ? task.getEstimatedHours() : 0);

            // Parse predecessor IDs (comma-separated)
            if (task.getPredecessorIds() != null && !task.getPredecessorIds().isEmpty()) {
                String[] preds = task.getPredecessorIds().split(",");
                for (String pred : preds) {
                    pred = pred.trim();
                    if (!pred.isEmpty()) {
                        successors.computeIfAbsent(pred, k -> new ArrayList<>()).add(id);
                        inDegree.merge(id, 1, Integer::sum);
                    }
                }
            }
        }

        // Topological sort using Kahn's algorithm
        Queue<String> queue = new LinkedList<>();
        for (Map.Entry<String, Integer> entry : inDegree.entrySet()) {
            if (entry.getValue() == 0) {
                queue.offer(entry.getKey());
            }
        }

        // Compute earliest finish time for each task (longest path)
        Map<String, Integer> earliestFinish = new HashMap<>();
        Map<String, String> predecessor = new HashMap<>();

        for (String id : inDegree.keySet()) {
            earliestFinish.put(id, duration.get(id));
        }

        while (!queue.isEmpty()) {
            String current = queue.poll();
            int currentFinish = earliestFinish.get(current);

            for (String succ : successors.getOrDefault(current, Collections.emptyList())) {
                int newFinish = currentFinish + duration.get(succ);
                if (newFinish > earliestFinish.get(succ)) {
                    earliestFinish.put(succ, newFinish);
                    predecessor.put(succ, current);
                }

                inDegree.merge(succ, -1, Integer::sum);
                if (inDegree.get(succ) == 0) {
                    queue.offer(succ);
                }
            }
        }

        // Find the task with maximum earliest finish (end of critical path)
        String endTask = null;
        int maxFinish = -1;
        for (Map.Entry<String, Integer> entry : earliestFinish.entrySet()) {
            if (entry.getValue() > maxFinish) {
                maxFinish = entry.getValue();
                endTask = entry.getKey();
            }
        }

        // Trace back to find the full critical path
        List<String> criticalPath = new ArrayList<>();
        String current = endTask;
        while (current != null) {
            criticalPath.add(current);
            current = predecessor.get(current);
        }
        Collections.reverse(criticalPath);

        return criticalPath;
    }
}
