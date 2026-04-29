package com.bank.updg.updg_resource.controller;

import com.bank.updg.common.model.ApiResponse;
import com.bank.updg.updg_resource.service.PositionMatchService;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/resource/match")
@RequiredArgsConstructor
public class PositionMatchController {

    private final PositionMatchService positionMatchService;

    @GetMapping
    public ApiResponse<List<Map<String, Object>>> matchByCriteria(
            @RequestParam(required = false) String skills,
            @RequestParam(required = false) String level,
            @RequestParam(required = false) String availability) {
        return ApiResponse.success(
                positionMatchService.matchByCriteria(skills, level, availability));
    }

    @PostMapping("/by-description")
    public ApiResponse<List<Map<String, Object>>> matchByDescription(
            @RequestBody Map<String, String> request) {
        String jobDescription = request.getOrDefault("jobDescription", "");
        return ApiResponse.success(positionMatchService.matchPosition(jobDescription));
    }
}
