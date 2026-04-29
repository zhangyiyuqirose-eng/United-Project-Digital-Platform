package com.bank.updg.updg_business.service;

import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.baomidou.mybatisplus.extension.service.IService;
import com.bank.updg.updg_business.model.entity.Supplier;

import java.util.Map;

public interface SupplierService extends IService<Supplier> {

    Supplier createSupplier(Supplier supplierData);

    void updateSupplier(String supplierId, Map<String, Object> data);

    Supplier getSupplier(String supplierId);

    Page<Supplier> listSuppliers(String type, String status, int page, int size);

    void blacklistSupplier(String supplierId, String reason);

    void evaluateSupplier(String supplierId, Double qualityScore, Double priceScore,
                          Double serviceScore, Double deliveryScore);
}
