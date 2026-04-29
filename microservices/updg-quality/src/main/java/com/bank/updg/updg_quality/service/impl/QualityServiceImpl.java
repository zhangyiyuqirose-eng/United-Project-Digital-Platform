package com.bank.updg.updg_quality.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import com.bank.updg.updg_quality.mapper.QualityDefectMapper;
import com.bank.updg.updg_quality.mapper.QualityMetricMapper;
import com.bank.updg.updg_quality.model.entity.QualityDefect;
import com.bank.updg.updg_quality.model.entity.QualityMetric;
import com.bank.updg.updg_quality.service.QualityService;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.UUID;

@Service
@RequiredArgsConstructor
public class QualityServiceImpl extends ServiceImpl<QualityDefectMapper, QualityDefect>
        implements QualityService {

    private final QualityMetricMapper metricMapper;

    @Override
    public QualityDefect createDefect(QualityDefect defectData) {
        if (defectData.getDefectId() == null || defectData.getDefectId().isEmpty()) {
            defectData.setDefectId(UUID.randomUUID().toString());
        }
        if (defectData.getStatus() == null) {
            defectData.setStatus("OPEN");
        }
        save(defectData);
        return defectData;
    }

    @Override
    public void updateDefect(String defectId, String status, String assignee, String fixVersion) {
        QualityDefect defect = getById(defectId);
        if (defect == null) {
            throw new RuntimeException("Defect not found: " + defectId);
        }
        if (status != null) {
            defect.setStatus(status);
        }
        if (assignee != null) {
            defect.setAssignee(assignee);
        }
        if (fixVersion != null) {
            defect.setFixVersion(fixVersion);
        }
        updateById(defect);
    }

    @Override
    public Page<QualityDefect> getDefectsByProject(String projectId, String status, int page, int size) {
        Page<QualityDefect> pageObj = new Page<>(page, size);
        LambdaQueryWrapper<QualityDefect> wrapper = new LambdaQueryWrapper<QualityDefect>()
                .eq(QualityDefect::getProjectId, projectId)
                .orderByDesc(QualityDefect::getFoundDate);
        if (status != null) {
            wrapper.eq(QualityDefect::getStatus, status);
        }
        return page(pageObj, wrapper);
    }

    @Override
    public QualityDefect getDefectDetail(String defectId) {
        return getById(defectId);
    }

    @Override
    public void closeDefect(String defectId) {
        QualityDefect defect = getById(defectId);
        if (defect == null) {
            throw new RuntimeException("Defect not found: " + defectId);
        }
        defect.setStatus("CLOSED");
        updateById(defect);
    }

    @Override
    public Map<String, Object> getDefectStats(String projectId) {
        List<QualityDefect> defects = list(new LambdaQueryWrapper<QualityDefect>()
                .eq(QualityDefect::getProjectId, projectId));

        Map<String, Object> stats = new HashMap<>();
        stats.put("total", defects.size());

        Map<String, Long> bySeverity = new HashMap<>();
        Map<String, Long> byStatus = new HashMap<>();
        for (QualityDefect d : defects) {
            bySeverity.merge(d.getSeverity() != null ? d.getSeverity() : "UNKNOWN", 1L, Long::sum);
            byStatus.merge(d.getStatus() != null ? d.getStatus() : "UNKNOWN", 1L, Long::sum);
        }
        stats.put("bySeverity", bySeverity);
        stats.put("byStatus", byStatus);
        return stats;
    }

    @Override
    public void recordMetric(String projectId, String metricName, Double value, Double target, String unit) {
        QualityMetric metric = QualityMetric.builder()
                .metricId(UUID.randomUUID().toString())
                .projectId(projectId)
                .metricName(metricName)
                .value(value)
                .target(target)
                .unit(unit)
                .build();
        metricMapper.insert(metric);
    }

    @Override
    public Page<QualityMetric> getMetrics(String projectId, int page, int size) {
        Page<QualityMetric> pageObj = new Page<>(page, size);
        return metricMapper.selectPage(pageObj, new LambdaQueryWrapper<QualityMetric>()
                .eq(QualityMetric::getProjectId, projectId)
                .orderByDesc(QualityMetric::getMeasuredDate));
    }
}
