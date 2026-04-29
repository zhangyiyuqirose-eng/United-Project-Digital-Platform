package com.bank.updg.updg_resource.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.bank.updg.common.exception.BusinessException;
import com.bank.updg.common.model.enums.ErrorCodeEnum;
import com.bank.updg.updg_resource.mapper.PerformanceEvalMapper;
import com.bank.updg.updg_resource.mapper.ResourceOutsourcingMapper;
import com.bank.updg.updg_resource.model.entity.PerformanceEval;
import com.bank.updg.updg_resource.model.entity.ResourceOutsourcing;
import com.bank.updg.updg_resource.service.PerformanceService;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
import java.util.*;
import java.util.stream.Collectors;
import java.util.UUID;

@Service
@RequiredArgsConstructor
public class PerformanceServiceImpl implements PerformanceService {

    private final PerformanceEvalMapper performanceEvalMapper;
    private final ResourceOutsourcingMapper resourceOutsourcingMapper;

    @Override
    public PerformanceEval createEval(PerformanceEval evalData) {
        evalData.setEvalId(UUID.randomUUID().toString().replace("-", ""));
        // Calculate overall score as average if not provided
        if (evalData.getOverallScore() == null) {
            int sum = 0;
            int count = 0;
            if (evalData.getQualityScore() != null) { sum += evalData.getQualityScore(); count++; }
            if (evalData.getEfficiencyScore() != null) { sum += evalData.getEfficiencyScore(); count++; }
            if (evalData.getAttitudeScore() != null) { sum += evalData.getAttitudeScore(); count++; }
            if (evalData.getSkillScore() != null) { sum += evalData.getSkillScore(); count++; }
            evalData.setOverallScore(count > 0 ? sum / count : 0);
        }
        evalData.setCreateTime(LocalDateTime.now());
        performanceEvalMapper.insert(evalData);
        return evalData;
    }

    @Override
    public PerformanceEval getEval(String staffId, String period) {
        return performanceEvalMapper.selectOne(
                new LambdaQueryWrapper<PerformanceEval>()
                        .eq(PerformanceEval::getStaffId, staffId)
                        .eq(period != null, PerformanceEval::getEvalPeriod, period)
                        .orderByDesc(PerformanceEval::getCreateTime)
                        .last("LIMIT 1"));
    }

    @Override
    public Page<PerformanceEval> listByStaff(String staffId, int page, int size) {
        Page<PerformanceEval> pageObj = new Page<>(page, size);
        return performanceEvalMapper.selectPage(pageObj,
                new LambdaQueryWrapper<PerformanceEval>()
                        .eq(PerformanceEval::getStaffId, staffId)
                        .orderByDesc(PerformanceEval::getCreateTime));
    }

    @Override
    public Map<String, Object> getAvgScores(String poolId) {
        // Get all staff in the resource pool
        List<ResourceOutsourcing> staff = resourceOutsourcingMapper.selectList(
                new LambdaQueryWrapper<ResourceOutsourcing>()
                        .eq(ResourceOutsourcing::getResourcePool, poolId));

        Set<String> staffIds = staff.stream()
                .map(ResourceOutsourcing::getStaffId)
                .collect(Collectors.toSet());

        if (staffIds.isEmpty()) {
            return Map.of("poolId", poolId, "count", 0);
        }

        // Get all evaluations for staff in this pool
        List<PerformanceEval> evals = performanceEvalMapper.selectList(
                new LambdaQueryWrapper<PerformanceEval>()
                        .in(PerformanceEval::getStaffId, staffIds));

        if (evals.isEmpty()) {
            return Map.of("poolId", poolId, "count", 0);
        }

        double avgQuality = evals.stream().mapToInt(e -> e.getQualityScore() != null ? e.getQualityScore() : 0).average().orElse(0);
        double avgEfficiency = evals.stream().mapToInt(e -> e.getEfficiencyScore() != null ? e.getEfficiencyScore() : 0).average().orElse(0);
        double avgAttitude = evals.stream().mapToInt(e -> e.getAttitudeScore() != null ? e.getAttitudeScore() : 0).average().orElse(0);
        double avgSkill = evals.stream().mapToInt(e -> e.getSkillScore() != null ? e.getSkillScore() : 0).average().orElse(0);
        double avgOverall = evals.stream().mapToInt(e -> e.getOverallScore() != null ? e.getOverallScore() : 0).average().orElse(0);

        Map<String, Object> result = new HashMap<>();
        result.put("poolId", poolId);
        result.put("count", evals.size());
        result.put("avgQuality", Math.round(avgQuality * 100.0) / 100.0);
        result.put("avgEfficiency", Math.round(avgEfficiency * 100.0) / 100.0);
        result.put("avgAttitude", Math.round(avgAttitude * 100.0) / 100.0);
        result.put("avgSkill", Math.round(avgSkill * 100.0) / 100.0);
        result.put("avgOverall", Math.round(avgOverall * 100.0) / 100.0);
        return result;
    }
}
