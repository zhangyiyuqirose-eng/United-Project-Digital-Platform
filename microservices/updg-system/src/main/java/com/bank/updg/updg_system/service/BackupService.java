package com.bank.updg.updg_system.service;

import java.util.List;
import java.util.Map;

/**
 * F-1410: Backup service.
 */
public interface BackupService {

    /**
     * Trigger a manual backup.
     * @param type FULL, PARTIAL, DATA_ONLY
     * @return backup record ID
     */
    String triggerBackup(String type);

    /**
     * Get backup history.
     * @param limit max records to return
     */
    List<Map<String, Object>> getHistory(int limit);

    /**
     * Get backup status by ID.
     */
    Map<String, Object> getStatus(String backupId);

    /**
     * Cancel a running backup.
     */
    void cancelBackup(String backupId);
}