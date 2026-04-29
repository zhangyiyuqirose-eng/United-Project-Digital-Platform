package com.bank.updg.updg_knowledge.controller;

import com.bank.updg.common.model.ApiResponse;
import com.bank.updg.updg_knowledge.service.KnowledgeDocService;
import com.bank.updg.updg_knowledge.service.RagService;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import java.util.Map;

@RestController
@RequestMapping("/api/knowledge")
@RequiredArgsConstructor
public class KnowledgeController {

    private final KnowledgeDocService docService;
    private final RagService ragService;

    @PostMapping("/upload")
    public ApiResponse upload(@RequestParam String title,
                              @RequestParam String category,
                              @RequestParam(required = false) String templateType,
                              @RequestParam MultipartFile file,
                              @RequestParam String createdBy) {
        docService.uploadDoc(title, category, templateType, file, createdBy);
        return ApiResponse.success("上传成功");
    }

    @GetMapping("/{docId}")
    public ApiResponse getById(@PathVariable String docId) {
        return ApiResponse.success(docService.getById(docId));
    }

    @GetMapping("/list")
    public ApiResponse listByCategory(@RequestParam(required = false) String category,
                                      @RequestParam(defaultValue = "1") int page,
                                      @RequestParam(defaultValue = "20") int size) {
        return ApiResponse.success(docService.listByCategory(category, page, size));
    }

    @PostMapping("/{docId}/new-version")
    public ApiResponse newVersion(@PathVariable String docId,
                                  @RequestParam MultipartFile file,
                                  @RequestParam String createdBy) {
        docService.newVersion(docId, file, createdBy);
        return ApiResponse.success("新版本创建成功");
    }

    @GetMapping("/{docId}/history")
    public ApiResponse getVersionHistory(@PathVariable String docId) {
        return ApiResponse.success(docService.getVersionHistory(docId));
    }

    @PostMapping("/rag/retrieve")
    public ApiResponse retrieve(@RequestBody Map<String, Object> body) {
        String query = (String) body.get("query");
        int topK = body.get("topK") != null ? ((Number) body.get("topK")).intValue() : 5;
        return ApiResponse.success(ragService.retrieve(query, topK));
    }
}
