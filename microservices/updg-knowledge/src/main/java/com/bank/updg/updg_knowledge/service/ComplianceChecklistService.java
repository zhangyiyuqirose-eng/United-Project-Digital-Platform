package com.bank.updg.updg_knowledge.service;

import com.baomidou.mybatisplus.extension.service.IService;
import com.bank.updg.updg_knowledge.model.entity.ComplianceChecklist;

import java.util.List;

public interface ComplianceChecklistService extends IService<ComplianceChecklist> {

    ComplianceChecklist createChecklist(ComplianceChecklist checklist);

    List<ComplianceChecklist> getByProjectId(String projectId);

    void updateProgress(String id, String completedItems, java.math.BigDecimal rate);
}
