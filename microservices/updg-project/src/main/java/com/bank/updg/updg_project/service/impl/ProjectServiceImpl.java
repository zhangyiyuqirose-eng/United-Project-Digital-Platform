package com.bank.updg.updg_project.service.impl;

import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import com.bank.updg.common.exception.BusinessException;
import com.bank.updg.common.model.enums.ErrorCodeEnum;
import com.bank.updg.updg_project.mapper.ProjectMapper;
import com.bank.updg.updg_project.model.entity.Project;
import com.bank.updg.updg_project.service.ProjectService;
import com.bank.updg.updg_project.util.EvmCalculator;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.*;
import java.util.UUID;

@Service
@RequiredArgsConstructor
public class ProjectServiceImpl extends ServiceImpl<ProjectMapper, Project> implements ProjectService {

    @Override
    public void initProject(Project project) {
        project.setProjectId(UUID.randomUUID().toString().replace("-", ""));
        project.setStatus("DRAFT");
        project.setEvmPv(BigDecimal.ZERO);
        project.setEvmEv(BigDecimal.ZERO);
        project.setEvmAc(BigDecimal.ZERO);
        project.setInitTime(LocalDateTime.now());
        save(project);
    }

    @Override
    public void updateProgress(String projectId, String wbsJson) {
        Project project = getById(projectId);
        if (project == null) throw new BusinessException(ErrorCodeEnum.PROJECT_NOT_FOUND);
        project.setWbsJson(wbsJson);
        updateById(project);
    }

    @Override
    public void submitChange(String projectId, String changeType, String content, String reason) {
        // TODO: create change record and trigger workflow
    }

    @Override
    public void closeProject(String projectId, String summary, String costSummary, String lessonsLearned) {
        Project project = getById(projectId);
        if (project == null) throw new BusinessException(ErrorCodeEnum.PROJECT_NOT_FOUND);
        project.setStatus("CLOSED");
        project.setActualEndTime(LocalDateTime.now());
        updateById(project);
    }

    @Override
    public Map<String, Object> getPortfolio() {
        // TODO: aggregate projects by type/status with EVM metrics
        return Map.of("totalProjects", count(), "activeProjects", 0);
    }

    @Override
    public void calculateEVM(String projectId, BigDecimal pv, BigDecimal ev, BigDecimal ac) {
        if (pv == null || ev == null || ac == null) {
            throw new BusinessException(ErrorCodeEnum.PARAM_ERROR, "pv, ev, ac are required");
        }
        Project project = getById(projectId);
        if (project == null) throw new BusinessException(ErrorCodeEnum.PROJECT_NOT_FOUND);

        Map<String, Object> result = EvmCalculator.buildResult(pv, ev, ac);
        project.setEvmPv(pv);
        project.setEvmEv(ev);
        project.setEvmAc(ac);
        project.setEvmCpi((BigDecimal) result.get("cpi"));
        project.setEvmSpi((BigDecimal) result.get("spi"));
        updateById(project);
    }

    @Override
    public Map<String, Object> generateWbs(String projectId) {
        Project project = getById(projectId);
        if (project == null) {
            throw new BusinessException(ErrorCodeEnum.PROJECT_NOT_FOUND);
        }

        // Standard WBS phases
        List<Map<String, Object>> phases = new ArrayList<>();

        // Phase 1: Initiation
        Map<String, Object> initiation = new LinkedHashMap<>();
        initiation.put("id", "1");
        initiation.put("name", "Initiation");
        initiation.put("children", List.of(
                Map.of("id", "1.1", "name", "Project Charter"),
                Map.of("id", "1.2", "name", "Stakeholder Identification"),
                Map.of("id", "1.3", "name", "Feasibility Study")));
        phases.add(initiation);

        // Phase 2: Planning
        Map<String, Object> planning = new LinkedHashMap<>();
        planning.put("id", "2");
        planning.put("name", "Planning");
        planning.put("children", List.of(
                Map.of("id", "2.1", "name", "Project Plan"),
                Map.of("id", "2.2", "name", "Requirements Specification"),
                Map.of("id", "2.3", "name", "Risk Assessment"),
                Map.of("id", "2.4", "name", "Resource Planning")));
        phases.add(planning);

        // Phase 3: Execution
        Map<String, Object> execution = new LinkedHashMap<>();
        execution.put("id", "3");
        execution.put("name", "Execution");
        execution.put("children", List.of(
                Map.of("id", "3.1", "name", "Design"),
                Map.of("id", "3.2", "name", "Development"),
                Map.of("id", "3.3", "name", "Integration"),
                Map.of("id", "3.4", "name", "Documentation")));
        phases.add(execution);

        // Phase 4: Testing
        Map<String, Object> testing = new LinkedHashMap<>();
        testing.put("id", "4");
        testing.put("name", "Testing");
        testing.put("children", List.of(
                Map.of("id", "4.1", "name", "Unit Testing"),
                Map.of("id", "4.2", "name", "Integration Testing"),
                Map.of("id", "4.3", "name", "User Acceptance Testing"),
                Map.of("id", "4.4", "name", "Bug Fixing")));
        phases.add(testing);

        // Phase 5: Delivery
        Map<String, Object> delivery = new LinkedHashMap<>();
        delivery.put("id", "5");
        delivery.put("name", "Delivery");
        delivery.put("children", List.of(
                Map.of("id", "5.1", "name", "Deployment"),
                Map.of("id", "5.2", "name", "User Training"),
                Map.of("id", "5.3", "name", "Project Handover"),
                Map.of("id", "5.4", "name", "Post-Delivery Review")));
        phases.add(delivery);

        Map<String, Object> wbs = new LinkedHashMap<>();
        wbs.put("projectId", projectId);
        wbs.put("projectName", project.getProjectName());
        wbs.put("phases", phases);

        // Save WBS JSON to project
        String wbsJson = wbs.toString();
        project.setWbsJson(wbsJson);
        updateById(project);

        return wbs;
    }
}
