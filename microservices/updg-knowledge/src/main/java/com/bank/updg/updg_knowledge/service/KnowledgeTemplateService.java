package com.bank.updg.updg_knowledge.service;

import com.bank.updg.updg_knowledge.model.entity.KnowledgeTemplate;

import java.util.List;

public interface KnowledgeTemplateService {

    List<KnowledgeTemplate> listAll();

    KnowledgeTemplate getById(String templateId);

    void create(KnowledgeTemplate template);
}
