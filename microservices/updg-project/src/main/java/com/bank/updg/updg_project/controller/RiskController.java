package com.bank.updg.updg_project.controller;

import com.bank.updg.common.model.ApiResponse;
import com.bank.updg.updg_project.model.entity.ProjectRisk;
import com.bank.updg.updg_project.service.RiskService;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

import java.math.BigDecimal;
import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/project/risk")
@RequiredArgsConstructor
public class RiskController {

    private final RiskService riskService;

    @PostMapping
    public ApiResponse createRisk(@RequestBody ProjectRisk risk) {
        return ApiResponse.success(riskService.createRisk(risk));
    }

    @GetMapping
    public ApiResponse<List<ProjectRisk>> listAll() {
        return ApiResponse.success(riskService.list());
    }

    @PutMapping("/{riskId}")
    public ApiResponse updateRisk(@PathVariable String riskId, @RequestBody ProjectRisk risk) {
        riskService.updateRisk(riskId, risk);
        return ApiResponse.success("Risk updated");
    }

    @GetMapping("/{riskId}")
    public ApiResponse getRisk(@PathVariable String riskId) {
        return ApiResponse.success(riskService.getRisk(riskId));
    }

    @GetMapping("/project/{projectId}")
    public ApiResponse listByProject(@PathVariable String projectId,
                                     @RequestParam(required = false) String status,
                                     @RequestParam(defaultValue = "1") int page,
                                     @RequestParam(defaultValue = "20") int size) {
        return ApiResponse.success(riskService.listByProject(projectId, status, page, size));
    }

    @GetMapping("/high-severity")
    public ApiResponse listHighSeverity() {
        return ApiResponse.success(riskService.listHighSeverityRisks());
    }

    @PutMapping("/{riskId}/status")
    public ApiResponse changeStatus(@PathVariable String riskId,
                                    @RequestParam String status,
                                    @RequestParam String userId) {
        riskService.changeStatus(riskId, status, userId);
        return ApiResponse.success("Risk status changed to " + status);
    }

    @GetMapping("/project/{projectId}/stats")
    public ApiResponse getRiskStats(@PathVariable String projectId) {
        return ApiResponse.success(riskService.getRiskStats(projectId));
    }

    @PostMapping("/{riskId}/assess")
    public ApiResponse assessRisk(@PathVariable String riskId) {
        BigDecimal score = riskService.assessRisk(riskId);
        return ApiResponse.success(Map.of("riskScore", score));
    }
}
