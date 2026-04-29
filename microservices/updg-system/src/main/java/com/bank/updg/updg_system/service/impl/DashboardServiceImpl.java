package com.bank.updg.updg_system.service.impl;

import com.bank.updg.updg_system.mapper.SysDeptMapper;
import com.bank.updg.updg_system.mapper.SysUserMapper;
import com.bank.updg.updg_system.model.entity.SysDept;
import com.bank.updg.updg_system.model.entity.SysUser;
import com.bank.updg.updg_system.service.DashboardService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.*;

/**
 * F-1301: Dashboard analytics service implementation.
 */
@Slf4j
@Service
@RequiredArgsConstructor
public class DashboardServiceImpl implements DashboardService {

    private final SysUserMapper sysUserMapper;
    private final SysDeptMapper sysDeptMapper;

    @Override
    public Map<String, Object> getOverview() {
        Map<String, Object> overview = new HashMap<>();

        // User statistics
        List<SysUser> users = sysUserMapper.selectList(null);
        overview.put("totalUsers", users.size());
        overview.put("activeUsers", users.stream()
                .filter(u -> u.getStatus() != null && u.getStatus() == 1)
                .count());

        // Department statistics
        List<SysDept> depts = sysDeptMapper.selectList(null);
        overview.put("totalDepts", depts.size());

        // System health indicators
        overview.put("systemHealth", "HEALTHY");
        overview.put("lastUpdateTime", LocalDateTime.now()
                .format(DateTimeFormatter.ISO_LOCAL_DATE_TIME));

        return overview;
    }

    @Override
    public List<Map<String, Object>> getTrend(String dimension, String period) {
        List<Map<String, Object>> trend = new ArrayList<>();

        // Generate trend data based on dimension and period
        // This is a placeholder implementation
        LocalDateTime now = LocalDateTime.now();
        int points = getPeriodPoints(period);

        for (int i = 0; i < points; i++) {
            Map<String, Object> point = new HashMap<>();
            point.put("time", now.minusDays(i).format(DateTimeFormatter.ISO_LOCAL_DATE));
            point.put("value", Math.random() * 100);
            point.put("dimension", dimension);
            trend.add(point);
        }

        return trend;
    }

    @Override
    public List<Map<String, Object>> getTopRisks(int limit) {
        List<Map<String, Object>> risks = new ArrayList<>();

        // Placeholder implementation for top risks
        // In real implementation, would query from project risk table
        for (int i = 0; i < Math.min(limit, 5); i++) {
            Map<String, Object> risk = new HashMap<>();
            risk.put("id", "RISK-" + (i + 1));
            risk.put("projectId", "PROJECT-" + (i + 1));
            risk.put("projectName", "Project " + (i + 1));
            risk.put("description", "Risk description " + (i + 1));
            risk.put("level", i < 2 ? "HIGH" : "MEDIUM");
            risk.put("status", "OPEN");
            risks.add(risk);
        }

        return risks;
    }

    private int getPeriodPoints(String period) {
        switch (period.toUpperCase()) {
            case "DAY":
                return 7;
            case "WEEK":
                return 4;
            case "MONTH":
                return 12;
            case "QUARTER":
                return 4;
            default:
                return 7;
        }
    }
}