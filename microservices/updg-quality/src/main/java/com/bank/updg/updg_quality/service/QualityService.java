package com.bank.updg.updg_quality.service;

import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.baomidou.mybatisplus.extension.service.IService;
import com.bank.updg.updg_quality.model.entity.QualityDefect;
import com.bank.updg.updg_quality.model.entity.QualityMetric;

import java.util.Map;

public interface QualityService extends IService<QualityDefect> {

    QualityDefect createDefect(QualityDefect defectData);

    void updateDefect(String defectId, String status, String assignee, String fixVersion);

    Page<QualityDefect> getDefectsByProject(String projectId, String status, int page, int size);

    QualityDefect getDefectDetail(String defectId);

    void closeDefect(String defectId);

    Map<String, Object> getDefectStats(String projectId);

    void recordMetric(String projectId, String metricName, Double value, Double target, String unit);

    Page<QualityMetric> getMetrics(String projectId, int page, int size);
}
