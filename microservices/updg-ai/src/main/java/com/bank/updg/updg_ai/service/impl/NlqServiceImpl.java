package com.bank.updg.updg_ai.service.impl;

import com.bank.updg.updg_ai.service.LlmClient;
import com.bank.updg.updg_ai.service.NlqService;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.util.Map;

@Service
@RequiredArgsConstructor
public class NlqServiceImpl implements NlqService {

    private final LlmClient llmClient;

    @Override
    public Map<String, Object> executeQuery(String question) {
        // TODO: convert NL question to SQL via LLM, execute query, return natural language answer
        String systemPrompt = "你是一个数据分析助手。用户会用自然语言提问，请将其转换为 SQL 查询并返回自然语言答案。";
        String answer = llmClient.chat(systemPrompt, question);

        return Map.of(
                "question", question,
                "answer", answer,
                "sql", "SELECT ... -- LLM-generated SQL placeholder",
                "dataSource", "MySQL"
        );
    }
}
