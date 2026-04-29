package com.bank.updg.updg_ai.service;

import java.util.Map;

/**
 * Natural Language Query service.
 * Converts user NL questions into SQL queries and returns natural language answers.
 */
public interface NlqService {

    /**
     * Parse a natural language query and return an answer.
     */
    Map<String, Object> executeQuery(String question);
}
