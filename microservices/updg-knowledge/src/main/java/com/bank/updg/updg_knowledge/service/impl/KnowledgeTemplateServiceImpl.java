package com.bank.updg.updg_knowledge.service.impl;

import com.bank.updg.updg_knowledge.mapper.KnowledgeTemplateMapper;
import com.bank.updg.updg_knowledge.model.entity.KnowledgeTemplate;
import com.bank.updg.updg_knowledge.service.KnowledgeTemplateService;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
@RequiredArgsConstructor
public class KnowledgeTemplateServiceImpl implements KnowledgeTemplateService {

    private final KnowledgeTemplateMapper templateMapper;

    @Override
    public List<KnowledgeTemplate> listAll() {
        return templateMapper.selectList(null);
    }

    @Override
    public KnowledgeTemplate getById(String templateId) {
        return templateMapper.selectById(templateId);
    }

    @Override
    public void create(KnowledgeTemplate template) {
        templateMapper.insert(template);
    }
}
