package com.bank.updg.updg_ai.service;

import java.util.Map;

/**
 * LLM client abstraction for calling external AI models (e.g. Qwen2-72B).
 */
public interface LlmClient {

    /**
     * Send a prompt to the LLM and get a text response.
     */
    String chat(String systemPrompt, String userPrompt);

    /**
     * Send a chat message with structured parameters.
     */
    String chatWithParams(String systemPrompt, String userPrompt, Map<String, Object> params);
}
