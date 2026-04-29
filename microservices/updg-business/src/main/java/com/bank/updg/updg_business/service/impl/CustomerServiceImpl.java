package com.bank.updg.updg_business.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import com.bank.updg.updg_business.mapper.CustomerMapper;
import com.bank.updg.updg_business.model.entity.Customer;
import com.bank.updg.updg_business.service.CustomerService;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.List;
import java.util.UUID;

@Service
@RequiredArgsConstructor
public class CustomerServiceImpl extends ServiceImpl<CustomerMapper, Customer>
        implements CustomerService {

    @Override
    public Customer createCustomer(Customer data) {
        if (data.getCustomerId() == null || data.getCustomerId().isEmpty()) {
            data.setCustomerId(UUID.randomUUID().toString());
        }
        if (data.getStatus() == null) {
            data.setStatus("ACTIVE");
        }
        String now = LocalDateTime.now().format(DateTimeFormatter.ISO_LOCAL_DATE_TIME);
        data.setCreatedAt(now);
        data.setUpdatedAt(now);
        save(data);
        return data;
    }

    @Override
    public void updateCustomer(String customerId, Customer data) {
        Customer existing = getById(customerId);
        if (existing == null) {
            throw new RuntimeException("Customer not found: " + customerId);
        }
        if (data.getName() != null) existing.setName(data.getName());
        if (data.getType() != null) existing.setType(data.getType());
        if (data.getIndustry() != null) existing.setIndustry(data.getIndustry());
        if (data.getContactPerson() != null) existing.setContactPerson(data.getContactPerson());
        if (data.getPhone() != null) existing.setPhone(data.getPhone());
        if (data.getEmail() != null) existing.setEmail(data.getEmail());
        if (data.getAddress() != null) existing.setAddress(data.getAddress());
        if (data.getCreditCode() != null) existing.setCreditCode(data.getCreditCode());
        if (data.getRating() != null) existing.setRating(data.getRating());
        if (data.getStatus() != null) existing.setStatus(data.getStatus());
        if (data.getNotes() != null) existing.setNotes(data.getNotes());
        existing.setUpdatedAt(LocalDateTime.now().format(DateTimeFormatter.ISO_LOCAL_DATE_TIME));
        updateById(existing);
    }

    @Override
    public Customer getCustomer(String customerId) {
        return getById(customerId);
    }

    @Override
    public Page<Customer> listCustomers(String type, String status, int page, int size) {
        Page<Customer> pageObj = new Page<>(page, size);
        LambdaQueryWrapper<Customer> wrapper = new LambdaQueryWrapper<Customer>()
                .orderByDesc(Customer::getCreatedAt);
        if (type != null) wrapper.eq(Customer::getType, type);
        if (status != null) wrapper.eq(Customer::getStatus, status);
        return page(pageObj, wrapper);
    }

    @Override
    public List<Customer> searchByKeyword(String keyword) {
        return list(new LambdaQueryWrapper<Customer>()
                .and(w -> w
                        .like(Customer::getName, keyword)
                        .or().like(Customer::getContactPerson, keyword)
                        .or().like(Customer::getIndustry, keyword))
                .orderByDesc(Customer::getCreatedAt));
    }

    @Override
    public List<Customer> getByIndustry(String industry) {
        return list(new LambdaQueryWrapper<Customer>()
                .eq(Customer::getIndustry, industry)
                .orderByDesc(Customer::getCreatedAt));
    }
}
