package com.bank.updg.updg_resource.controller;

import com.bank.updg.common.model.ApiResponse;
import com.bank.updg.updg_resource.service.SettlementService;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

import java.util.Map;

@RestController
@RequestMapping("/api/resource/settlement")
@RequiredArgsConstructor
public class SettlementController {

    private final SettlementService settlementService;

    @PostMapping("/generate")
    public ApiResponse<Map<String, Object>> generate(
            @RequestParam String projectId,
            @RequestParam String yearMonth) {
        return ApiResponse.success(settlementService.generateMonthlySettlement(projectId, yearMonth));
    }

    @GetMapping("/summary")
    public ApiResponse<Map<String, Object>> summary(
            @RequestParam String projectId,
            @RequestParam String yearMonth) {
        return ApiResponse.success(settlementService.getMonthlySummary(projectId, yearMonth));
    }
}
