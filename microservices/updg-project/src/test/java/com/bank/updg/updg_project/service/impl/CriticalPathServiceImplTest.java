package com.bank.updg.updg_project.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.bank.updg.updg_project.mapper.ProjectTaskMapper;
import com.bank.updg.updg_project.model.entity.ProjectTask;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import java.util.Collections;
import java.util.List;

import static org.assertj.core.api.Assertions.assertThat;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.when;

@ExtendWith(MockitoExtension.class)
class CriticalPathServiceImplTest {

    @Mock
    private ProjectTaskMapper taskMapper;

    private CriticalPathServiceImpl service;

    @BeforeEach
    void setUp() {
        service = new CriticalPathServiceImpl(taskMapper);
    }

    @Test
    @DisplayName("findCriticalPath - empty project returns empty list")
    void findCriticalPath_emptyProject_returnsEmpty() {
        when(taskMapper.selectList(any())).thenReturn(Collections.emptyList());

        List<String> result = service.findCriticalPath("proj1");

        assertThat(result).isEmpty();
    }

    @Test
    @DisplayName("findCriticalPath - linear chain A->B->C returns all tasks")
    void findCriticalPath_linearChain_returnsAllTasks() {
        List<ProjectTask> tasks = List.of(
                task("A", null, 3),
                task("B", "A", 5),
                task("C", "B", 2)
        );
        when(taskMapper.selectList(any())).thenReturn(tasks);

        List<String> result = service.findCriticalPath("proj1");

        assertThat(result).containsExactly("A", "B", "C");
    }

    @Test
    @DisplayName("findCriticalPath - single task returns that task")
    void findCriticalPath_singleTask_returnsThatTask() {
        when(taskMapper.selectList(any())).thenReturn(List.of(
                task("only", null, 4)
        ));

        List<String> result = service.findCriticalPath("proj1");

        assertThat(result).containsExactly("only");
    }

    @Test
    @DisplayName("findCriticalPath - parallel paths picks longest path")
    void findCriticalPath_parallelPaths_picksLongest() {
        // A(3) -> B(5) = 8
        // A(3) -> C(2) = 5
        // Critical path should be A -> B
        List<ProjectTask> tasks = List.of(
                task("A", null, 3),
                task("B", "A", 5),
                task("C", "A", 2)
        );
        when(taskMapper.selectList(any())).thenReturn(tasks);

        List<String> result = service.findCriticalPath("proj1");

        assertThat(result).endsWith("B");
    }

    @Test
    @DisplayName("findCriticalPath - tasks without dependencies all start")
    void findCriticalPath_independentTasks_longestSingle() {
        List<ProjectTask> tasks = List.of(
                task("X", null, 10),
                task("Y", null, 5),
                task("Z", null, 3)
        );
        when(taskMapper.selectList(any())).thenReturn(tasks);

        List<String> result = service.findCriticalPath("proj1");

        // Longest single task is X with 10 hours
        assertThat(result).containsExactly("X");
    }

    private ProjectTask task(String id, String predecessorIds, Integer hours) {
        return ProjectTask.builder()
                .taskId(id)
                .projectId("proj1")
                .taskName(id)
                .estimatedHours(hours)
                .predecessorIds(predecessorIds)
                .status("NOT_STARTED")
                .build();
    }
}
