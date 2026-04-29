package com.bank.updg.updg_business.service;

import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.baomidou.mybatisplus.extension.service.IService;
import com.bank.updg.updg_business.model.entity.Customer;

import java.util.List;

public interface CustomerService extends IService<Customer> {

    Customer createCustomer(Customer data);

    void updateCustomer(String customerId, Customer data);

    Customer getCustomer(String customerId);

    Page<Customer> listCustomers(String type, String status, int page, int size);

    List<Customer> searchByKeyword(String keyword);

    List<Customer> getByIndustry(String industry);
}
