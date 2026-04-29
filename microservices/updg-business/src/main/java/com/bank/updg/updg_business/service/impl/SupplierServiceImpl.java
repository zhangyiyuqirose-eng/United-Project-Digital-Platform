package com.bank.updg.updg_business.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import com.bank.updg.updg_business.mapper.SupplierMapper;
import com.bank.updg.updg_business.model.entity.Supplier;
import com.bank.updg.updg_business.service.SupplierService;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.util.Map;
import java.util.UUID;

@Service
@RequiredArgsConstructor
public class SupplierServiceImpl extends ServiceImpl<SupplierMapper, Supplier>
        implements SupplierService {

    @Override
    public Supplier createSupplier(Supplier supplierData) {
        if (supplierData.getSupplierId() == null || supplierData.getSupplierId().isEmpty()) {
            supplierData.setSupplierId(UUID.randomUUID().toString());
        }
        if (supplierData.getSupplierCode() == null || supplierData.getSupplierCode().isEmpty()) {
            supplierData.setSupplierCode("SUP-" + System.currentTimeMillis());
        }
        if (supplierData.getStatus() == null) {
            supplierData.setStatus("ACTIVE");
        }
        if (supplierData.getRating() == null) {
            supplierData.setRating("C");
        }
        save(supplierData);
        return supplierData;
    }

    @Override
    public void updateSupplier(String supplierId, Map<String, Object> data) {
        Supplier supplier = getById(supplierId);
        if (supplier == null) {
            throw new RuntimeException("Supplier not found: " + supplierId);
        }
        if (data.containsKey("supplierName")) {
            supplier.setSupplierName((String) data.get("supplierName"));
        }
        if (data.containsKey("contactPerson")) {
            supplier.setContactPerson((String) data.get("contactPerson"));
        }
        if (data.containsKey("contactPhone")) {
            supplier.setContactPhone((String) data.get("contactPhone"));
        }
        if (data.containsKey("contactEmail")) {
            supplier.setContactEmail((String) data.get("contactEmail"));
        }
        if (data.containsKey("type")) {
            supplier.setType((String) data.get("type"));
        }
        if (data.containsKey("rating")) {
            supplier.setRating((String) data.get("rating"));
        }
        if (data.containsKey("qualifications")) {
            supplier.setQualifications((String) data.get("qualifications"));
        }
        if (data.containsKey("address")) {
            supplier.setAddress((String) data.get("address"));
        }
        updateById(supplier);
    }

    @Override
    public Supplier getSupplier(String supplierId) {
        return getById(supplierId);
    }

    @Override
    public Page<Supplier> listSuppliers(String type, String status, int page, int size) {
        Page<Supplier> pageObj = new Page<>(page, size);
        LambdaQueryWrapper<Supplier> wrapper = new LambdaQueryWrapper<Supplier>()
                .orderByDesc(Supplier::getCreateTime);
        if (type != null) {
            wrapper.eq(Supplier::getType, type);
        }
        if (status != null) {
            wrapper.eq(Supplier::getStatus, status);
        }
        return page(pageObj, wrapper);
    }

    @Override
    public void blacklistSupplier(String supplierId, String reason) {
        Supplier supplier = getById(supplierId);
        if (supplier == null) {
            throw new RuntimeException("Supplier not found: " + supplierId);
        }
        supplier.setStatus("BLACKLISTED");
        updateById(supplier);
    }

    @Override
    public void evaluateSupplier(String supplierId, Double qualityScore, Double priceScore,
                                 Double serviceScore, Double deliveryScore) {
        Supplier supplier = getById(supplierId);
        if (supplier == null) {
            throw new RuntimeException("Supplier not found: " + supplierId);
        }
        double avg = (qualityScore + priceScore + serviceScore + deliveryScore) / 4.0;
        String rating;
        if (avg >= 90) {
            rating = "A";
        } else if (avg >= 75) {
            rating = "B";
        } else if (avg >= 60) {
            rating = "C";
        } else {
            rating = "D";
        }
        supplier.setRating(rating);
        updateById(supplier);
    }
}
