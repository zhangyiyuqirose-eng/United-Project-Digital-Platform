package com.bank.updg.updg_business.controller;

import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.bank.updg.common.model.ApiResponse;
import com.bank.updg.updg_business.model.entity.Quotation;
import com.bank.updg.updg_business.service.QuotationService;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/business/quotation")
@RequiredArgsConstructor
public class QuotationController {

    private final QuotationService quotationService;

    @PostMapping
    public ApiResponse<Quotation> create(@RequestBody Quotation data) {
        return ApiResponse.success(quotationService.createQuotation(data));
    }

    @PutMapping("/{id}")
    public ApiResponse<Void> update(@PathVariable String id, @RequestBody Quotation data) {
        quotationService.updateQuotation(id, data);
        return ApiResponse.success();
    }

    @GetMapping("/{id}")
    public ApiResponse<Quotation> getDetail(@PathVariable String id) {
        return ApiResponse.success(quotationService.getQuotation(id));
    }

    @GetMapping("/list")
    public ApiResponse<Page<Quotation>> list(
            @RequestParam(required = false) String opportunityId,
            @RequestParam(required = false) String status,
            @RequestParam(defaultValue = "1") int page,
            @RequestParam(defaultValue = "10") int size) {
        return ApiResponse.success(quotationService.listQuotations(opportunityId, status, page, size));
    }

    @PostMapping("/{id}/send")
    public ApiResponse<Void> send(@PathVariable String id) {
        quotationService.sendQuotation(id);
        return ApiResponse.success();
    }

    @PostMapping("/{id}/accept")
    public ApiResponse<Void> accept(@PathVariable String id) {
        quotationService.acceptQuotation(id);
        return ApiResponse.success();
    }

    @PostMapping("/{id}/reject")
    public ApiResponse<Void> reject(@PathVariable String id) {
        quotationService.rejectQuotation(id);
        return ApiResponse.success();
    }
}
