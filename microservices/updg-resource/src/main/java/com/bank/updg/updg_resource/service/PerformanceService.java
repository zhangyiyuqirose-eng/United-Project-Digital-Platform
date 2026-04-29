package com.bank.updg.updg_resource.service;

import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.bank.updg.updg_resource.model.entity.PerformanceEval;

import java.util.Map;

public interface PerformanceService {

    PerformanceEval createEval(PerformanceEval evalData);

    PerformanceEval getEval(String staffId, String period);

    Page<PerformanceEval> listByStaff(String staffId, int page, int size);

    Map<String, Object> getAvgScores(String poolId);
}
