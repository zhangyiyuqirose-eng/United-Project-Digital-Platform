package com.bank.updg.updg_file.service;

/**
 * Service for archiving project documents.
 */
public interface ArchiveService {

    /**
     * Archive all documents belonging to a project.
     * Marks files as archived and moves to archive bucket.
     */
    void archiveProjectDocuments(String projectId);
}
