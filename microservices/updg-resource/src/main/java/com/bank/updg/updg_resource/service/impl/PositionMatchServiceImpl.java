package com.bank.updg.updg_resource.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.bank.updg.updg_resource.model.entity.ResourcePool;
import com.bank.updg.updg_resource.service.PositionMatchService;
import com.bank.updg.updg_resource.service.ResourcePoolService;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.util.ArrayList;
import java.util.Comparator;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

@Service
@RequiredArgsConstructor
public class PositionMatchServiceImpl implements PositionMatchService {

    private final ResourcePoolService resourcePoolService;

    @Override
    public List<Map<String, Object>> matchPosition(String jobDescription) {
        // In production: use NLP/AI to parse job description and match against resource skills.
        // Placeholder: return all available resources with basic scoring.
        List<ResourcePool> all = resourcePoolService.listAll();
        List<Map<String, Object>> candidates = new ArrayList<>();

        String lower = jobDescription.toLowerCase();
        for (ResourcePool r : all) {
            int score = 20; // base availability score
            if (r.getDescription() != null) {
                String desc = r.getDescription().toLowerCase();
                String[] keywords = lower.split("[\\s,;]+");
                for (String kw : keywords) {
                    if (kw.length() > 2 && desc.contains(kw)) {
                        score += 15;
                    }
                }
            }
            score = Math.min(score, 100);
            Map<String, Object> entry = new HashMap<>();
            entry.put("poolId", r.getPoolId());
            entry.put("poolName", r.getPoolName());
            entry.put("matchScore", score);
            entry.put("availability", "AVAILABLE");
            candidates.add(entry);
        }
        candidates.sort(Comparator.comparingInt(
                (Map<String, Object> c) -> (Integer) c.get("matchScore")).reversed());
        return candidates;
    }

    @Override
    public List<Map<String, Object>> matchByCriteria(String skills, String level, String availability) {
        List<ResourcePool> all = resourcePoolService.listAll();
        List<Map<String, Object>> results = new ArrayList<>();

        for (ResourcePool r : all) {
            int score = 50;
            if (skills != null && !skills.isEmpty()) {
                if (r.getDescription() != null && r.getDescription().toLowerCase()
                        .contains(skills.toLowerCase())) {
                    score += 30;
                }
            }
            if (level != null && !level.isEmpty()) {
                if (r.getDescription() != null && r.getDescription().toLowerCase()
                        .contains(level.toLowerCase())) {
                    score += 20;
                }
            }
            score = Math.min(score, 100);
            Map<String, Object> entry = new HashMap<>();
            entry.put("poolId", r.getPoolId());
            entry.put("poolName", r.getPoolName());
            entry.put("matchScore", score);
            entry.put("description", r.getDescription());
            results.add(entry);
        }
        results.sort(Comparator.comparingInt(
                (Map<String, Object> c) -> (Integer) c.get("matchScore")).reversed());
        return results;
    }
}
