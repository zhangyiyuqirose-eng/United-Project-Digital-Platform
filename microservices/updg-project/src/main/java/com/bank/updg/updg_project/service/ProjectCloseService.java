package com.bank.updg.updg_project.service;

/**
 * Service for managing project close settlement.
 */
public interface ProjectCloseService {

    /**
     * Complete the project close process: mark as CLOSED, settle costs, archive docs, notify.
     */
    void completeClose(String closeId);
}
