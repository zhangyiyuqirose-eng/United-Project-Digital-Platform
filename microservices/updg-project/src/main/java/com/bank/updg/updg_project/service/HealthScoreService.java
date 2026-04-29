package com.bank.updg.updg_project.service;

import java.math.BigDecimal;

/**
 * Service for computing project health score (0-100).
 * F-113: Schedule variance (30%), Cost variance (30%),
 * Risk level (20%), Task completion (20%).
 */
public interface HealthScoreService {

    /**
     * Compute and return the health score for a project.
     */
    BigDecimal computeHealthScore(String projectId);
}
