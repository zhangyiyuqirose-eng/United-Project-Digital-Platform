package com.bank.updg.updg_business.controller;

import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.bank.updg.common.model.ApiResponse;
import com.bank.updg.updg_business.model.entity.Customer;
import com.bank.updg.updg_business.service.CustomerService;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/business/customer")
@RequiredArgsConstructor
public class CustomerController {

    private final CustomerService customerService;

    @PostMapping
    public ApiResponse<Customer> create(@RequestBody Customer data) {
        return ApiResponse.success(customerService.createCustomer(data));
    }

    @PutMapping("/{id}")
    public ApiResponse<Void> update(@PathVariable String id, @RequestBody Customer data) {
        customerService.updateCustomer(id, data);
        return ApiResponse.success();
    }

    @GetMapping("/{id}")
    public ApiResponse<Customer> getDetail(@PathVariable String id) {
        return ApiResponse.success(customerService.getCustomer(id));
    }

    @GetMapping("/list")
    public ApiResponse<Page<Customer>> list(
            @RequestParam(required = false) String type,
            @RequestParam(required = false) String status,
            @RequestParam(defaultValue = "1") int page,
            @RequestParam(defaultValue = "10") int size) {
        return ApiResponse.success(customerService.listCustomers(type, status, page, size));
    }

    @GetMapping("/search")
    public ApiResponse<List<Customer>> search(@RequestParam String keyword) {
        return ApiResponse.success(customerService.searchByKeyword(keyword));
    }

    @GetMapping("/by-industry")
    public ApiResponse<List<Customer>> getByIndustry(@RequestParam String industry) {
        return ApiResponse.success(customerService.getByIndustry(industry));
    }
}
