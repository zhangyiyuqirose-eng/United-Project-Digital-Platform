package com.bank.updg.updg_ai.service.impl;

import com.bank.updg.updg_ai.service.AiDocGenerationService;
import com.bank.updg.updg_ai.service.LlmClient;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.util.Map;

@Service
@RequiredArgsConstructor
public class AiDocGenerationServiceImpl implements AiDocGenerationService {

    private final LlmClient llmClient;

    @Override
    public String generateDocument(String templateType, Map<String, Object> projectParams) {
        String systemPrompt = "你是一个专业的项目管理助手，请根据提供的项目参数生成" + templateType + "文档。";
        return llmClient.chatWithParams(systemPrompt, "请生成项目文档", projectParams);
    }

    @Override
    public byte[] generateReport(String projectId, String reportType) {
        // TODO: fetch project data, generate Excel report via Apache POI
        return new byte[0];
    }
}
