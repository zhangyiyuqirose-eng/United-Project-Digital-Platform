package com.bank.updg.updg_ai.service;

import java.util.Map;

/**
 * AI document generation service.
 * Generates project documents from templates + project parameters via LLM.
 */
public interface AiDocGenerationService {

    /**
     * Generate a project document (e.g. charter, plan, report) based on template and project data.
     */
    String generateDocument(String templateType, Map<String, Object> projectParams);

    /**
     * Generate an Excel report from project data.
     */
    byte[] generateReport(String projectId, String reportType);
}
