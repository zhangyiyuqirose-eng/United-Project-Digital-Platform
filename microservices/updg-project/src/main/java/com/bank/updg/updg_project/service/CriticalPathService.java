package com.bank.updg.updg_project.service;

import java.util.List;

/**
 * Critical path analysis service (F-303).
 * Computes the longest path through task dependencies using topological sort.
 */
public interface CriticalPathService {

    /**
     * Returns the list of task IDs on the critical path for a project.
     */
    List<String> findCriticalPath(String projectId);
}
