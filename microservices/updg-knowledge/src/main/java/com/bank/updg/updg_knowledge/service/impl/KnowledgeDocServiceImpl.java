package com.bank.updg.updg_knowledge.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.bank.updg.updg_knowledge.mapper.KnowledgeDocMapper;
import com.bank.updg.updg_knowledge.model.entity.KnowledgeDoc;
import com.bank.updg.updg_knowledge.service.KnowledgeDocService;
import com.bank.updg.updg_knowledge.service.RagService;
import io.minio.MinioClient;
import io.minio.PutObjectArgs;
import lombok.RequiredArgsConstructor;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.multipart.MultipartFile;

import java.time.LocalDateTime;
import java.util.List;
import java.util.UUID;

@Service
@RequiredArgsConstructor
public class KnowledgeDocServiceImpl implements KnowledgeDocService {

    private final KnowledgeDocMapper docMapper;
    private final RagService ragService;
    private final MinioClient minioClient;

    @Value("${minio.bucket:knowledge-docs}")
    private String bucket;

    @Override
    @Transactional
    public void uploadDoc(String title, String category, String templateType, MultipartFile file, String createdBy) {
        String docId = UUID.randomUUID().toString().replace("-", "");
        String objectName = category + "/" + docId + "_" + sanitizeFileName(file.getOriginalFilename());

        try {
            minioClient.putObject(
                    PutObjectArgs.builder()
                            .bucket(bucket)
                            .object(objectName)
                            .stream(file.getInputStream(), file.getSize(), -1)
                            .contentType(file.getContentType())
                            .build()
            );
        } catch (Exception e) {
            throw new RuntimeException("Failed to upload document to MinIO: " + e.getMessage(), e);
        }

        String filePath = "/knowledge/" + objectName;
        KnowledgeDoc doc = KnowledgeDoc.builder()
                .docId(docId)
                .title(title)
                .category(category)
                .templateType(templateType)
                .filePath(filePath)
                .version("1.0")
                .createdBy(createdBy)
                .versionNum(1)
                .createTime(LocalDateTime.now())
                .build();
        docMapper.insert(doc);

        // Index document content for RAG search
        try {
            String content = new String(file.getBytes(), java.nio.charset.StandardCharsets.UTF_8);
            ragService.indexDocument(docId, content);
        } catch (Exception e) {
            // Non-critical: doc is stored even if indexing fails
        }
    }

    @Override
    public KnowledgeDoc getById(String docId) {
        return docMapper.selectById(docId);
    }

    @Override
    public Page<KnowledgeDoc> listByCategory(String category, int page, int size) {
        Page<KnowledgeDoc> pageObj = new Page<>(page, size);
        LambdaQueryWrapper<KnowledgeDoc> wrapper = new LambdaQueryWrapper<>();
        if (category != null && !category.isBlank()) {
            wrapper.eq(KnowledgeDoc::getCategory, category);
        }
        wrapper.orderByDesc(KnowledgeDoc::getCreateTime);
        return docMapper.selectPage(pageObj, wrapper);
    }

    @Override
    @Transactional
    public void newVersion(String docId, MultipartFile file, String createdBy) {
        KnowledgeDoc existing = docMapper.selectById(docId);
        if (existing == null) {
            throw new IllegalArgumentException("文档不存在: " + docId);
        }

        String newDocId = UUID.randomUUID().toString().replace("-", "");
        String objectName = existing.getCategory() + "/" + newDocId + "_" + sanitizeFileName(file.getOriginalFilename());

        try {
            minioClient.putObject(
                    PutObjectArgs.builder()
                            .bucket(bucket)
                            .object(objectName)
                            .stream(file.getInputStream(), file.getSize(), -1)
                            .contentType(file.getContentType())
                            .build()
            );
        } catch (Exception e) {
            throw new RuntimeException("Failed to upload document to MinIO: " + e.getMessage(), e);
        }

        String filePath = "/knowledge/" + objectName;
        KnowledgeDoc newDoc = KnowledgeDoc.builder()
                .docId(newDocId)
                .title(existing.getTitle())
                .category(existing.getCategory())
                .templateType(existing.getTemplateType())
                .filePath(filePath)
                .version((existing.getVersionNum() + 1) + ".0")
                .createdBy(createdBy)
                .versionNum(existing.getVersionNum() + 1)
                .createTime(LocalDateTime.now())
                .build();
        docMapper.insert(newDoc);
    }

    @Override
    public List<KnowledgeDoc> getVersionHistory(String docId) {
        KnowledgeDoc base = docMapper.selectById(docId);
        if (base == null) {
            return List.of();
        }
        LambdaQueryWrapper<KnowledgeDoc> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(KnowledgeDoc::getTitle, base.getTitle())
               .eq(KnowledgeDoc::getCategory, base.getCategory())
               .orderByDesc(KnowledgeDoc::getVersionNum);
        return docMapper.selectList(wrapper);
    }

    private String sanitizeFileName(String fileName) {
        if (fileName == null || fileName.isBlank()) {
            return "unnamed";
        }
        return fileName.replaceAll("[^a-zA-Z0-9._\\-\\u4e00-\\u9fff]", "_");
    }
}
