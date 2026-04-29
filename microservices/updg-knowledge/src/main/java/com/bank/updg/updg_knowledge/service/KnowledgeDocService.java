package com.bank.updg.updg_knowledge.service;

import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.bank.updg.updg_knowledge.model.entity.KnowledgeDoc;
import org.springframework.web.multipart.MultipartFile;

import java.util.List;

public interface KnowledgeDocService {

    void uploadDoc(String title, String category, String templateType, MultipartFile file, String createdBy);

    KnowledgeDoc getById(String docId);

    Page<KnowledgeDoc> listByCategory(String category, int page, int size);

    /**
     * Create a new version of an existing document.
     */
    void newVersion(String docId, MultipartFile file, String createdBy);

    List<KnowledgeDoc> getVersionHistory(String docId);
}
