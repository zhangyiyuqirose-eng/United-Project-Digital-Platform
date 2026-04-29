package com.bank.updg.updg_project.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.bank.updg.common.exception.BusinessException;
import com.bank.updg.updg_project.mapper.ProjectMapper;
import com.bank.updg.updg_project.mapper.ProjectRiskMapper;
import com.bank.updg.updg_project.mapper.ProjectTaskMapper;
import com.bank.updg.updg_project.model.entity.Project;
import com.bank.updg.updg_project.model.entity.ProjectRisk;
import com.bank.updg.updg_project.model.entity.ProjectTask;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import java.math.BigDecimal;
import java.util.List;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.when;

@ExtendWith(MockitoExtension.class)
class HealthScoreServiceImplTest {

    @Mock
    private ProjectMapper projectMapper;

    @Mock
    private ProjectRiskMapper riskMapper;

    @Mock
    private ProjectTaskMapper taskMapper;

    private HealthScoreServiceImpl service;

    @BeforeEach
    void setUp() {
        service = new HealthScoreServiceImpl(projectMapper, taskMapper, riskMapper);
    }

    @Test
    @DisplayName("computeHealthScore - throws when project not found")
    void computeHealthScore_projectNotFound_throws() {
        when(projectMapper.selectById("nonexistent")).thenReturn(null);

        assertThatThrownBy(() -> service.computeHealthScore("nonexistent"))
                .isInstanceOf(BusinessException.class)
                .hasMessageContaining("Project not found");
    }

    @Test
    @DisplayName("computeHealthScore - perfect project returns 100")
    void computeHealthScore_perfectProject_returns100() {
        Project project = healthyProject();
        project.setEvmSpi(new BigDecimal("1.05"));
        project.setEvmCpi(new BigDecimal("1.02"));
        when(projectMapper.selectById("proj1")).thenReturn(project);
        when(riskMapper.selectList(any())).thenReturn(List.of());
        when(taskMapper.selectList(any())).thenReturn(List.of(
                taskWithStatus("DONE"),
                taskWithStatus("DONE"),
                taskWithStatus("DONE")
        ));

        BigDecimal score = service.computeHealthScore("proj1");

        assertThat(score).isEqualByComparingTo(new BigDecimal("100.00"));
    }

    @Test
    @DisplayName("computeHealthScore - SPI below 1.0 penalizes schedule")
    void computeHealthScore_spiBelow1_penalizesSchedule() {
        Project project = healthyProject();
        project.setEvmSpi(new BigDecimal("0.75"));
        project.setEvmCpi(new BigDecimal("1.0"));
        when(projectMapper.selectById("proj1")).thenReturn(project);
        when(riskMapper.selectList(any())).thenReturn(List.of());
        when(taskMapper.selectList(any())).thenReturn(List.of(
                taskWithStatus("DONE"),
                taskWithStatus("IN_PROGRESS")
        ));

        BigDecimal score = service.computeHealthScore("proj1");

        // SPI 0.75 * 100 = 75 for schedule (30% weight), rest is 100
        // 75*0.30 + 100*0.30 + 100*0.20 + 50*0.20 = 22.5 + 30 + 20 + 10 = 82.5
        assertThat(score).isLessThan(new BigDecimal("100"));
    }

    @Test
    @DisplayName("computeHealthScore - critical risks penalize score")
    void computeHealthScore_criticalRisks_penalizes() {
        Project project = healthyProject();
        project.setEvmSpi(new BigDecimal("1.0"));
        project.setEvmCpi(new BigDecimal("1.0"));
        when(projectMapper.selectById("proj1")).thenReturn(project);

        ProjectRisk criticalRisk = ProjectRisk.builder()
                .riskId("r1")
                .severity("CRITICAL")
                .status("IDENTIFIED")
                .build();
        when(riskMapper.selectList(any())).thenReturn(List.of(criticalRisk));
        when(taskMapper.selectList(any())).thenReturn(List.of(
                taskWithStatus("DONE"),
                taskWithStatus("DONE")
        ));

        BigDecimal score = service.computeHealthScore("proj1");

        // 100*0.30 + 100*0.30 + 75*0.20 + 100*0.20 = 30+30+15+20 = 95
        assertThat(score).isEqualByComparingTo(new BigDecimal("95.00"));
    }

    @Test
    @DisplayName("computeHealthScore - no tasks returns 100 for task score")
    void computeHealthScore_noTasks_returns100ForTask() {
        Project project = healthyProject();
        project.setEvmSpi(new BigDecimal("1.0"));
        project.setEvmCpi(new BigDecimal("1.0"));
        when(projectMapper.selectById("proj1")).thenReturn(project);
        when(riskMapper.selectList(any())).thenReturn(List.of());
        when(taskMapper.selectList(any())).thenReturn(List.of());

        BigDecimal score = service.computeHealthScore("proj1");

        assertThat(score).isEqualByComparingTo(new BigDecimal("100.00"));
    }

    @Test
    @DisplayName("computeHealthScore - multiple risk severities deduct correctly")
    void computeHealthScore_multipleRiskSeverities_deductCorrectly() {
        Project project = healthyProject();
        project.setEvmSpi(new BigDecimal("1.0"));
        project.setEvmCpi(new BigDecimal("1.0"));
        when(projectMapper.selectById("proj1")).thenReturn(project);

        List<ProjectRisk> risks = List.of(
                riskWithSeverity("CRITICAL"),
                riskWithSeverity("HIGH"),
                riskWithSeverity("MEDIUM")
        );
        when(riskMapper.selectList(any())).thenReturn(risks);
        when(taskMapper.selectList(any())).thenReturn(List.of(
                taskWithStatus("DONE")
        ));

        BigDecimal score = service.computeHealthScore("proj1");

        // Risk deductions: 25 + 15 + 5 = 45, risk score = 55
        // 100*0.30 + 100*0.30 + 55*0.20 + 100*0.20 = 30+30+11+20 = 91
        assertThat(score).isEqualByComparingTo(new BigDecimal("91.00"));
    }

    private Project healthyProject() {
        Project p = new Project();
        p.setProjectId("proj1");
        p.setStatus("ACTIVE");
        return p;
    }

    private ProjectTask taskWithStatus(String status) {
        return ProjectTask.builder()
                .taskId("t-" + status.toLowerCase())
                .status(status)
                .build();
    }

    private ProjectRisk riskWithSeverity(String severity) {
        return ProjectRisk.builder()
                .riskId("r-" + severity.toLowerCase())
                .severity(severity)
                .status("IDENTIFIED")
                .build();
    }
}
