package com.bank.updg.updg_business.controller;

import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.bank.updg.common.model.ApiResponse;
import com.bank.updg.updg_business.model.entity.Supplier;
import com.bank.updg.updg_business.service.SupplierService;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

import java.util.Map;

@RestController
@RequestMapping("/api/business/supplier")
@RequiredArgsConstructor
public class SupplierController {

    private final SupplierService supplierService;

    @PostMapping("/create")
    public ApiResponse<Supplier> createNew(@RequestBody Supplier supplierData) {
        return ApiResponse.success(supplierService.createSupplier(supplierData));
    }

    @PostMapping
    public ApiResponse<Supplier> create(@RequestBody Supplier supplierData) {
        return ApiResponse.success(supplierService.createSupplier(supplierData));
    }

    @PutMapping("/{id}")
    public ApiResponse<Void> update(@PathVariable String id, @RequestBody Map<String, Object> data) {
        supplierService.updateSupplier(id, data);
        return ApiResponse.success();
    }

    @GetMapping("/{id}")
    public ApiResponse<Supplier> getDetail(@PathVariable String id) {
        return ApiResponse.success(supplierService.getSupplier(id));
    }

    @GetMapping("/list")
    public ApiResponse<Page<Supplier>> list(
            @RequestParam(required = false) String type,
            @RequestParam(required = false) String status,
            @RequestParam(defaultValue = "1") int page,
            @RequestParam(defaultValue = "10") int size) {
        return ApiResponse.success(supplierService.listSuppliers(type, status, page, size));
    }

    @PutMapping("/{id}/blacklist")
    public ApiResponse<Void> blacklist(
            @PathVariable String id,
            @RequestParam String reason) {
        supplierService.blacklistSupplier(id, reason);
        return ApiResponse.success();
    }

    @PostMapping("/{id}/evaluate")
    public ApiResponse<Void> evaluate(
            @PathVariable String id,
            @RequestParam Double qualityScore,
            @RequestParam Double priceScore,
            @RequestParam Double serviceScore,
            @RequestParam Double deliveryScore) {
        supplierService.evaluateSupplier(id, qualityScore, priceScore, serviceScore, deliveryScore);
        return ApiResponse.success();
    }
}
