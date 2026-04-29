package com.bank.updg.updg_workflow.controller;

import com.bank.updg.common.model.ApiResponse;
import com.bank.updg.updg_workflow.model.entity.ProcessDefinition;
import com.bank.updg.updg_workflow.service.ProcessConfigService;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

import java.util.List;

/**
 * F-1001: Approval process configuration management.
 * Stores approval flow definitions as JSON.
 */
@RestController
@RequestMapping("/api/workflow/process-config")
@RequiredArgsConstructor
public class ProcessConfigController {

    private final ProcessConfigService processConfigService;

    @PostMapping
    public ApiResponse<ProcessDefinition> create(@RequestBody ProcessDefinition config) {
        return ApiResponse.success(processConfigService.createConfig(config));
    }

    @PutMapping("/{id}")
    public ApiResponse<ProcessDefinition> update(@PathVariable String id,
                                                  @RequestBody ProcessDefinition config) {
        return ApiResponse.success(processConfigService.updateConfig(id, config));
    }

    @GetMapping
    public ApiResponse<List<ProcessDefinition>> listAll() {
        return ApiResponse.success(processConfigService.listAll());
    }

    @GetMapping("/key/{processKey}")
    public ApiResponse<ProcessDefinition> getByKey(@PathVariable String processKey) {
        return ApiResponse.success(processConfigService.getByKey(processKey));
    }

    @DeleteMapping("/{id}")
    public ApiResponse<Void> delete(@PathVariable String id) {
        processConfigService.deleteConfig(id);
        return ApiResponse.success();
    }
}
