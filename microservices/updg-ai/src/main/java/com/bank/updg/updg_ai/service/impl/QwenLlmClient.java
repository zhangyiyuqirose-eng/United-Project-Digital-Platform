package com.bank.updg.updg_ai.service.impl;

import com.bank.updg.updg_ai.service.LlmClient;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.web.reactive.function.client.WebClient;
import reactor.core.publisher.Mono;

import java.util.Map;

/**
 * Qwen2-72B LLM client via Spring AI / DashScope API.
 */
@Service
public class QwenLlmClient implements LlmClient {

    @Value("${ai.dashscope.api-key:}")
    private String apiKey;

    @Value("${ai.dashscope.base-url:https://dashscope.aliyuncs.com}")
    private String baseUrl;

    private WebClient getWebClient() {
        return WebClient.builder()
                .baseUrl(baseUrl)
                .defaultHeader("Authorization", "Bearer " + apiKey)
                .defaultHeader("Content-Type", "application/json")
                .build();
    }

    @Override
    public String chat(String systemPrompt, String userPrompt) {
        // TODO: integrate Spring AI or DashScope SDK for production use
        return "AI service not yet configured — configure ai.dashscope.api-key in application.yml";
    }

    @Override
    public String chatWithParams(String systemPrompt, String userPrompt, Map<String, Object> params) {
        String enrichedPrompt = userPrompt + "\n\nParameters:\n" + params;
        return chat(systemPrompt, enrichedPrompt);
    }
}
