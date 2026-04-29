package com.bank.updg.updg_knowledge.service;

import java.util.List;
import java.util.Map;

/**
 * RAG retrieval service backed by Milvus vector database.
 */
public interface RagService {

    /**
     * Index a document into the vector store.
     */
    void indexDocument(String docId, String content);

    /**
     * Retrieve top-K most relevant documents for a query.
     */
    List<Map<String, Object>> retrieve(String query, int topK);

    /**
     * Delete a document from the vector store.
     */
    void deleteDocument(String docId);
}
