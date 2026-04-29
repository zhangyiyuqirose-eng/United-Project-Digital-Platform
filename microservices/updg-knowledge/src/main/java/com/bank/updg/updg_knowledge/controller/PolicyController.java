package com.bank.updg.updg_knowledge.controller;

import com.bank.updg.common.model.ApiResponse;
import com.bank.updg.updg_knowledge.service.KnowledgeDocService;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

/**
 * F-1007: Policy/Regulation library.
 * Reuses knowledge management with POLICY category filter.
 */
@RestController
@RequestMapping("/api/knowledge/policy")
@RequiredArgsConstructor
public class PolicyController {

    private final KnowledgeDocService docService;

    @GetMapping("/list")
    public ApiResponse listPolicies(
            @RequestParam(defaultValue = "1") int page,
            @RequestParam(defaultValue = "20") int size) {
        return ApiResponse.success(docService.listByCategory("POLICY", page, size));
    }

    @GetMapping("/{docId}")
    public ApiResponse getPolicy(@PathVariable String docId) {
        return ApiResponse.success(docService.getById(docId));
    }
}
