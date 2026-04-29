package com.bank.updg.updg_knowledge.controller;

import com.bank.updg.common.model.ApiResponse;
import com.bank.updg.updg_knowledge.model.entity.ComplianceChecklist;
import com.bank.updg.updg_knowledge.service.ComplianceChecklistService;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

import java.math.BigDecimal;
import java.util.List;
import java.util.Map;

/**
 * F-1008: Compliance checklist management.
 */
@RestController
@RequestMapping("/api/knowledge/compliance")
@RequiredArgsConstructor
public class ComplianceChecklistController {

    private final ComplianceChecklistService checklistService;

    @PostMapping
    public ApiResponse<ComplianceChecklist> create(@RequestBody ComplianceChecklist checklist) {
        return ApiResponse.success(checklistService.createChecklist(checklist));
    }

    @GetMapping("/project/{projectId}")
    public ApiResponse<List<ComplianceChecklist>> getByProject(@PathVariable String projectId) {
        return ApiResponse.success(checklistService.getByProjectId(projectId));
    }

    @PutMapping("/{id}/progress")
    public ApiResponse<Void> updateProgress(@PathVariable String id,
                                            @RequestBody Map<String, Object> body) {
        String completedItems = (String) body.get("completedItems");
        BigDecimal rate = body.get("rate") != null
                ? new BigDecimal(body.get("rate").toString())
                : BigDecimal.ZERO;
        checklistService.updateProgress(id, completedItems, rate);
        return ApiResponse.success();
    }
}
