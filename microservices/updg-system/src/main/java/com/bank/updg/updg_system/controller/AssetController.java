package com.bank.updg.updg_system.controller;

import com.bank.updg.common.model.ApiResponse;
import com.bank.updg.updg_system.model.entity.Asset;
import com.bank.updg.updg_system.service.AssetService;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

/**
 * F-1105: Asset management.
 */
@RestController
@RequestMapping("/api/system/asset")
@RequiredArgsConstructor
public class AssetController {

    private final AssetService assetService;

    @PostMapping
    public ApiResponse<Asset> create(@RequestBody Asset asset) {
        return ApiResponse.success(assetService.createAsset(asset));
    }

    @GetMapping
    public ApiResponse<List<Asset>> listAll() {
        return ApiResponse.success(assetService.listAll());
    }

    @PostMapping("/{id}/assign")
    public ApiResponse<Void> assign(@PathVariable String id,
                                    @RequestBody Map<String, String> body) {
        assetService.assignAsset(id, body.get("assignedTo"), body.get("projectId"));
        return ApiResponse.success();
    }

    @PostMapping("/{id}/return")
    public ApiResponse<Void> returnAsset(@PathVariable String id) {
        assetService.returnAsset(id);
        return ApiResponse.success();
    }

    @PostMapping("/{id}/damaged")
    public ApiResponse<Void> markDamaged(@PathVariable String id) {
        assetService.markDamaged(id);
        return ApiResponse.success();
    }
}
