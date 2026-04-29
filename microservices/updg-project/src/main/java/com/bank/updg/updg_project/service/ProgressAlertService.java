package com.bank.updg.updg_project.service;

import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.bank.updg.updg_project.model.entity.ProgressAlert;

import java.util.List;

/**
 * Progress alert service (F-304).
 * Compares project actual progress vs expected progress based on timeline.
 * Creates alerts when deviation exceeds 15%.
 */
public interface ProgressAlertService {

    /**
     * Check all active projects and create progress alerts for those
     * with deviation > 15%.
     */
    List<ProgressAlert> checkAllProjects();

    /**
     * Check a single project and create alert if deviation > 15%.
     */
    ProgressAlert checkProject(String projectId);

    /**
     * Get all active progress alerts.
     */
    List<ProgressAlert> getActiveAlerts();

    /**
     * Paginated alerts by project.
     */
    Page<ProgressAlert> listByProject(String projectId, int page, int size);

    /**
     * Resolve an alert.
     */
    void resolveAlert(String alertId);
}
