package com.bank.updg.updg_system.controller;

import com.bank.updg.common.model.ApiResponse;
import com.bank.updg.updg_system.model.entity.SysConfig;
import com.bank.updg.updg_system.service.SysConfigService;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/system/config")
@RequiredArgsConstructor
public class SysConfigController {

    private final SysConfigService sysConfigService;

    /**
     * Get configuration by key
     */
    @GetMapping("/{key}")
    public ApiResponse<SysConfig> getConfig(@PathVariable String key) {
        return ApiResponse.success(sysConfigService.getConfig(key));
    }

    /**
     * Set or update a configuration
     */
    @PutMapping("/{key}")
    public ApiResponse<Void> setConfig(
            @PathVariable String key,
            @RequestBody Map<String, String> body) {
        String value = body.get("value");
        String type = body.get("type");
        String description = body.get("description");
        sysConfigService.setConfig(key, value, type, description);
        return ApiResponse.success();
    }

    /**
     * List configurations by type
     */
    @GetMapping("/list")
    public ApiResponse<List<SysConfig>> listConfigs(
            @RequestParam(required = false) String type) {
        return ApiResponse.success(sysConfigService.listConfigs(type));
    }

    /**
     * Delete a configuration
     */
    @DeleteMapping("/{id}")
    public ApiResponse<Void> deleteConfig(@PathVariable Long id) {
        sysConfigService.deleteConfig(id);
        return ApiResponse.success();
    }
}
