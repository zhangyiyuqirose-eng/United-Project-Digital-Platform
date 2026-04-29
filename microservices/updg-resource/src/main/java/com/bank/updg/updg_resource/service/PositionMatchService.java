package com.bank.updg.updg_resource.service;

import java.util.List;
import java.util.Map;

public interface PositionMatchService {

    /**
     * Match a job description to available resources.
     * Scores candidates by skill match, availability, and experience.
     * Returns ranked list of candidates with match scores.
     */
    List<Map<String, Object>> matchPosition(String jobDescription);

    /**
     * Match resources by skills, level, and availability.
     */
    List<Map<String, Object>> matchByCriteria(String skills, String level, String availability);
}
