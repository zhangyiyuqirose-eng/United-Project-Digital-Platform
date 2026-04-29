package com.bank.updg.updg_ai.controller;

import com.bank.updg.common.model.ApiResponse;
import com.bank.updg.updg_ai.service.AiDocGenerationService;
import com.bank.updg.updg_ai.service.NlqService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.Map;

@RestController
@RequestMapping("/api/ai")
@RequiredArgsConstructor
public class AiController {

    private final AiDocGenerationService docGenerationService;
    private final NlqService nlqService;

    @PostMapping("/generate-doc")
    public ApiResponse generateDoc(@RequestBody Map<String, Object> body) {
        String templateType = (String) body.get("templateType");
        @SuppressWarnings("unchecked")
        Map<String, Object> params = (Map<String, Object>) body.get("params");
        String content = docGenerationService.generateDocument(templateType, params);
        return ApiResponse.success(Map.of("content", content));
    }

    @PostMapping("/nlq")
    public ApiResponse nlq(@RequestBody Map<String, String> body) {
        String question = body.get("question");
        return ApiResponse.success(nlqService.executeQuery(question));
    }

    @GetMapping("/report/{projectId}")
    public ResponseEntity<byte[]> generateReport(@PathVariable String projectId,
                                                  @RequestParam(defaultValue = "summary") String reportType) {
        byte[] data = docGenerationService.generateReport(projectId, reportType);
        return ResponseEntity.ok()
                .header(HttpHeaders.CONTENT_DISPOSITION, "attachment; filename=\"report.xlsx\"")
                .contentType(MediaType.APPLICATION_OCTET_STREAM)
                .body(data);
    }
}
