package com.bank.updg.updg_business.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import com.bank.updg.updg_business.mapper.BusinessOpportunityMapper;
import com.bank.updg.updg_business.model.entity.BusinessOpportunity;
import com.bank.updg.updg_business.service.BusinessOpportunityService;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
public class BusinessOpportunityServiceImpl extends ServiceImpl<BusinessOpportunityMapper, BusinessOpportunity>
        implements BusinessOpportunityService {

    @Override
    public BusinessOpportunity createOpportunity(BusinessOpportunity data) {
        if (data.getOpportunityId() == null || data.getOpportunityId().isEmpty()) {
            data.setOpportunityId(UUID.randomUUID().toString());
        }
        if (data.getStage() == null) {
            data.setStage("LEAD");
        }
        if (data.getProbability() == null) {
            data.setProbability(10);
        }
        String now = LocalDateTime.now().format(DateTimeFormatter.ISO_LOCAL_DATE_TIME);
        data.setCreatedAt(now);
        data.setUpdatedAt(now);
        save(data);
        return data;
    }

    @Override
    public void updateOpportunity(String opportunityId, Map<String, Object> data) {
        BusinessOpportunity opp = getById(opportunityId);
        if (opp == null) {
            throw new RuntimeException("Opportunity not found: " + opportunityId);
        }
        if (data.containsKey("name")) opp.setName((String) data.get("name"));
        if (data.containsKey("customerId")) opp.setCustomerId((String) data.get("customerId"));
        if (data.containsKey("stage")) opp.setStage((String) data.get("stage"));
        if (data.containsKey("estimatedValue")) {
            opp.setEstimatedValue((BigDecimal) data.get("estimatedValue"));
        }
        if (data.containsKey("probability")) {
            opp.setProbability((Integer) data.get("probability"));
        }
        if (data.containsKey("ownerId")) opp.setOwnerId((String) data.get("ownerId"));
        if (data.containsKey("expectedCloseDate")) {
            opp.setExpectedCloseDate((String) data.get("expectedCloseDate"));
        }
        if (data.containsKey("source")) opp.setSource((String) data.get("source"));
        if (data.containsKey("description")) opp.setDescription((String) data.get("description"));
        if (data.containsKey("projectId")) opp.setProjectId((String) data.get("projectId"));
        opp.setUpdatedAt(LocalDateTime.now().format(DateTimeFormatter.ISO_LOCAL_DATE_TIME));
        updateById(opp);
    }

    @Override
    public BusinessOpportunity getOpportunity(String opportunityId) {
        return getById(opportunityId);
    }

    @Override
    public Page<BusinessOpportunity> listOpportunities(String customerId, String stage, int page, int size) {
        Page<BusinessOpportunity> pageObj = new Page<>(page, size);
        LambdaQueryWrapper<BusinessOpportunity> wrapper = new LambdaQueryWrapper<BusinessOpportunity>()
                .orderByDesc(BusinessOpportunity::getCreatedAt);
        if (customerId != null) {
            wrapper.eq(BusinessOpportunity::getCustomerId, customerId);
        }
        if (stage != null) {
            wrapper.eq(BusinessOpportunity::getStage, stage);
        }
        return page(pageObj, wrapper);
    }

    @Override
    public void advanceStage(String opportunityId, String nextStage) {
        BusinessOpportunity opp = getById(opportunityId);
        if (opp == null) {
            throw new RuntimeException("Opportunity not found: " + opportunityId);
        }
        opp.setStage(nextStage);
        opp.setUpdatedAt(LocalDateTime.now().format(DateTimeFormatter.ISO_LOCAL_DATE_TIME));
        updateById(opp);
    }

    @Override
    public List<Map<String, Object>> getPipeline() {
        List<BusinessOpportunity> all = list(new LambdaQueryWrapper<BusinessOpportunity>()
                .isNotNull(BusinessOpportunity::getEstimatedValue));

        List<String> stages = List.of("LEAD", "QUALIFIED", "PROPOSAL", "NEGOTIATION", "WON", "LOST");
        List<Map<String, Object>> pipeline = new ArrayList<>();

        for (String stage : stages) {
            List<BusinessOpportunity> stageOpps = all.stream()
                    .filter(o -> stage.equals(o.getStage()))
                    .collect(Collectors.toList());
            BigDecimal weightedValue = stageOpps.stream()
                    .map(o -> o.getEstimatedValue().multiply(
                            BigDecimal.valueOf(o.getProbability() != null ? o.getProbability() : 0)
                    ).divide(BigDecimal.valueOf(100)))
                    .reduce(BigDecimal.ZERO, BigDecimal::add);
            Map<String, Object> entry = new LinkedHashMap<>();
            entry.put("stage", stage);
            entry.put("count", stageOpps.size());
            entry.put("totalValue", stageOpps.stream()
                    .map(BusinessOpportunity::getEstimatedValue)
                    .reduce(BigDecimal.ZERO, BigDecimal::add));
            entry.put("weightedValue", weightedValue);
            pipeline.add(entry);
        }
        return pipeline;
    }
}
