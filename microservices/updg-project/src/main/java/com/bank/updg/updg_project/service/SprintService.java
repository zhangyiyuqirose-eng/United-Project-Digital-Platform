package com.bank.updg.updg_project.service;

import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.bank.updg.updg_project.model.entity.Sprint;

import java.math.BigDecimal;
import java.util.List;

/**
 * Sprint management service (F-309).
 */
public interface SprintService {

    /** Create a new sprint. */
    Sprint createSprint(Sprint sprint);

    /** Update sprint details. */
    void updateSprint(String sprintId, Sprint sprint);

    /** Get sprint by ID. */
    Sprint getSprint(String sprintId);

    /** List sprints for a project. */
    List<Sprint> listByProject(String projectId);

    /** Paginated sprints for a project. */
    Page<Sprint> pageByProject(String projectId, int page, int size);

    /** Complete a sprint. */
    void completeSprint(String sprintId, BigDecimal velocity);

    /** Cancel a sprint. */
    void cancelSprint(String sprintId);

    /** Get active sprint for a project. */
    Sprint getActiveSprint(String projectId);
}
