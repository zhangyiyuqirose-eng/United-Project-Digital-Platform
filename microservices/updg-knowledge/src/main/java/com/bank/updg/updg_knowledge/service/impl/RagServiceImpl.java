package com.bank.updg.updg_knowledge.service.impl;

import com.bank.updg.updg_knowledge.service.RagService;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * Placeholder RAG implementation.
 * Replace with actual Milvus integration when vector DB is deployed.
 */
@Service
@RequiredArgsConstructor
public class RagServiceImpl implements RagService {

    @Override
    public void indexDocument(String docId, String content) {
        // TODO: integrate Milvus SDK — embed content and upsert vector
    }

    @Override
    public List<Map<String, Object>> retrieve(String query, int topK) {
        // TODO: embed query, search Milvus, return top-K results with docId + score + snippet
        List<Map<String, Object>> results = new ArrayList<>();
        for (int i = 0; i < topK; i++) {
            Map<String, Object> item = new HashMap<>();
            item.put("docId", "placeholder_" + i);
            item.put("score", 0.0);
            item.put("snippet", "Milvus not yet configured");
            results.add(item);
        }
        return results;
    }

    @Override
    public void deleteDocument(String docId) {
        // TODO: delete from Milvus by docId
    }
}
