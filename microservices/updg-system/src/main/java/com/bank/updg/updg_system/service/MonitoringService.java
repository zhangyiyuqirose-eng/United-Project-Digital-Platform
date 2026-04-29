package com.bank.updg.updg_system.service;

import java.util.Map;

/**
 * F-1411: Monitoring service.
 */
public interface MonitoringService {

    /**
     * Check system health status.
     */
    Map<String, Object> checkHealth();

    /**
     * Get system metrics.
     */
    Map<String, Object> getMetrics();

    /**
     * Check specific service status.
     */
    Map<String, Object> checkServiceStatus(String serviceName);

    /**
     * Get alert history.
     */
    Map<String, Object> getAlertHistory(int limit);
}