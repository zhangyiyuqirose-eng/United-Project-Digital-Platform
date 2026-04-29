package com.bank.updg.updg_knowledge.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import com.bank.updg.updg_knowledge.mapper.ComplianceChecklistMapper;
import com.bank.updg.updg_knowledge.model.entity.ComplianceChecklist;
import com.bank.updg.updg_knowledge.service.ComplianceChecklistService;
import org.springframework.stereotype.Service;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.List;
import java.util.UUID;

@Service
public class ComplianceChecklistServiceImpl
        extends ServiceImpl<ComplianceChecklistMapper, ComplianceChecklist>
        implements ComplianceChecklistService {

    @Override
    public ComplianceChecklist createChecklist(ComplianceChecklist checklist) {
        checklist.setId(UUID.randomUUID().toString().replace("-", ""));
        save(checklist);
        return checklist;
    }

    @Override
    public List<ComplianceChecklist> getByProjectId(String projectId) {
        LambdaQueryWrapper<ComplianceChecklist> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(ComplianceChecklist::getProjectId, projectId);
        return list(wrapper);
    }

    @Override
    public void updateProgress(String id, String completedItems, BigDecimal rate) {
        ComplianceChecklist checklist = getById(id);
        if (checklist != null) {
            checklist.setCompletedItems(completedItems);
            checklist.setCompletionRate(rate);
            checklist.setCheckedAt(LocalDateTime.now());
            updateById(checklist);
        }
    }
}
