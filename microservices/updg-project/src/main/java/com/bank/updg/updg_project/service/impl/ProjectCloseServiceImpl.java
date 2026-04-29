package com.bank.updg.updg_project.service.impl;

import com.bank.updg.common.exception.BusinessException;
import com.bank.updg.common.model.enums.ErrorCodeEnum;
import com.bank.updg.updg_project.mapper.ProjectCloseMapper;
import com.bank.updg.updg_project.model.entity.ProjectClose;
import com.bank.updg.updg_project.service.ProjectCloseService;
import com.bank.updg.updg_project.service.ProjectService;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;

/**
 * Implementation of project close settlement.
 * Marks project CLOSED, triggers cost settlement, archives documents, sends notification.
 */
@Service
@RequiredArgsConstructor
public class ProjectCloseServiceImpl implements ProjectCloseService {

    private final ProjectCloseMapper projectCloseMapper;
    private final ProjectService projectService;

    @Override
    public void completeClose(String closeId) {
        ProjectClose close = projectCloseMapper.selectById(closeId);
        if (close == null) {
            throw new BusinessException(ErrorCodeEnum.NOT_FOUND, "Project close record not found: " + closeId);
        }

        // 1. Mark project as CLOSED
        projectService.closeProject(
                close.getProjectId(),
                close.getSummary(),
                close.getCostSummary(),
                close.getLessonsLearned());

        // 2. Finalize cost settlement timestamp
        close.setCostSummary("{\"settledAt\":\"" + LocalDateTime.now() + "\",\"status\":\"SETTLED\"}");
        projectCloseMapper.updateById(close);

        // 3. Archive project documents (delegated to file service via internal call)
        // TODO: integrate with updg-file archive endpoint

        // 4. Send completion notification
        // TODO: integrate with updg-notify notification service
    }
}
