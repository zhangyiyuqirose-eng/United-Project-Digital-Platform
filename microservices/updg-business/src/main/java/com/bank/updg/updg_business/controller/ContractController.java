package com.bank.updg.updg_business.controller;

import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.bank.updg.common.model.ApiResponse;
import com.bank.updg.updg_business.model.entity.Contract;
import com.bank.updg.updg_business.service.ContractService;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/business/contract")
@RequiredArgsConstructor
public class ContractController {

    private final ContractService contractService;

    @PostMapping("/create")
    public ApiResponse<Contract> create(@RequestBody Contract contractData) {
        return ApiResponse.success(contractService.createContract(contractData));
    }

    @PostMapping
    public ApiResponse<Contract> createDefault(@RequestBody Contract contractData) {
        return ApiResponse.success(contractService.createContract(contractData));
    }

    @PutMapping("/{id}")
    public ApiResponse<Void> update(@PathVariable String id, @RequestBody Map<String, Object> data) {
        contractService.updateContract(id, data);
        return ApiResponse.success();
    }

    @GetMapping("/{id}")
    public ApiResponse<Contract> getDetail(@PathVariable String id) {
        return ApiResponse.success(contractService.getContract(id));
    }

    @GetMapping("/list")
    public ApiResponse<Page<Contract>> list(
            @RequestParam(required = false) String projectId,
            @RequestParam(required = false) String type,
            @RequestParam(required = false) String status,
            @RequestParam(defaultValue = "1") int page,
            @RequestParam(defaultValue = "10") int size) {
        return ApiResponse.success(contractService.listContracts(projectId, type, status, page, size));
    }

    @GetMapping("/expiring")
    public ApiResponse<List<Contract>> getExpiringContracts(
            @RequestParam(defaultValue = "30") int days) {
        return ApiResponse.success(contractService.getExpiringContracts(days));
    }

    @PutMapping("/{id}/archive")
    public ApiResponse<Void> archive(@PathVariable String id) {
        contractService.archiveContract(id);
        return ApiResponse.success();
    }

    @PutMapping("/{id}/terminate")
    public ApiResponse<Void> terminate(
            @PathVariable String id,
            @RequestParam String reason) {
        contractService.terminateContract(id, reason);
        return ApiResponse.success();
    }
}
