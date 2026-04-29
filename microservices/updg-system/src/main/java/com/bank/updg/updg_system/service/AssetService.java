package com.bank.updg.updg_system.service;

import com.baomidou.mybatisplus.extension.service.IService;
import com.bank.updg.updg_system.model.entity.Asset;

import java.util.List;

public interface AssetService extends IService<Asset> {

    Asset createAsset(Asset asset);

    List<Asset> listAll();

    void assignAsset(String id, String assignedTo, String projectId);

    void returnAsset(String id);

    void markDamaged(String id);
}
