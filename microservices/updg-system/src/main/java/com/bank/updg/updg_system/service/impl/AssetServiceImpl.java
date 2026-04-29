package com.bank.updg.updg_system.service.impl;

import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import com.bank.updg.updg_system.mapper.AssetMapper;
import com.bank.updg.updg_system.model.entity.Asset;
import com.bank.updg.updg_system.service.AssetService;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
import java.util.List;
import java.util.UUID;

@Service
public class AssetServiceImpl extends ServiceImpl<AssetMapper, Asset>
        implements AssetService {

    @Override
    public Asset createAsset(Asset asset) {
        asset.setId(UUID.randomUUID().toString().replace("-", ""));
        asset.setStatus("AVAILABLE");
        asset.setCreatedAt(LocalDateTime.now());
        save(asset);
        return asset;
    }

    @Override
    public List<Asset> listAll() {
        return list();
    }

    @Override
    public void assignAsset(String id, String assignedTo, String projectId) {
        Asset asset = getById(id);
        if (asset != null) {
            asset.setAssignedTo(assignedTo);
            asset.setProjectId(projectId);
            asset.setStatus("ASSIGNED");
            updateById(asset);
        }
    }

    @Override
    public void returnAsset(String id) {
        Asset asset = getById(id);
        if (asset != null) {
            asset.setAssignedTo(null);
            asset.setProjectId(null);
            asset.setStatus("RETURNED");
            updateById(asset);
        }
    }

    @Override
    public void markDamaged(String id) {
        Asset asset = getById(id);
        if (asset != null) {
            asset.setStatus("DAMAGED");
            updateById(asset);
        }
    }
}
