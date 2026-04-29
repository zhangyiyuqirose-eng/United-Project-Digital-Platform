package com.bank.updg.updg_project.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.bank.updg.common.exception.BusinessException;
import com.bank.updg.common.model.enums.ErrorCodeEnum;
import com.bank.updg.updg_project.mapper.PreInitiationMapper;
import com.bank.updg.updg_project.model.entity.PreInitiation;
import com.bank.updg.updg_project.service.PreInitiationService;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
import java.util.UUID;

@Service
@RequiredArgsConstructor
public class PreInitiationServiceImpl implements PreInitiationService {

    private final PreInitiationMapper preInitiationMapper;

    @Override
    public PreInitiation createPreInitiation(PreInitiation data) {
        data.setPreId(UUID.randomUUID().toString().replace("-", ""));
        data.setStatus("DRAFT");
        data.setCreateTime(LocalDateTime.now());
        data.setUpdateTime(LocalDateTime.now());
        preInitiationMapper.insert(data);
        return data;
    }

    @Override
    public void submitPreInitiation(String preId) {
        PreInitiation existing = preInitiationMapper.selectById(preId);
        if (existing == null) {
            throw new BusinessException(ErrorCodeEnum.PARAM_ERROR, "Pre-initiation not found: " + preId);
        }
        if (!"DRAFT".equals(existing.getStatus()) && !"REJECTED".equals(existing.getStatus())) {
            throw new BusinessException(ErrorCodeEnum.PARAM_ERROR, "Only DRAFT or REJECTED applications can be submitted");
        }
        existing.setStatus("SUBMITTED");
        existing.setSubmitTime(LocalDateTime.now());
        existing.setUpdateTime(LocalDateTime.now());
        preInitiationMapper.updateById(existing);
    }

    @Override
    public void approvePreInitiation(String preId, boolean approved, String comment) {
        PreInitiation existing = preInitiationMapper.selectById(preId);
        if (existing == null) {
            throw new BusinessException(ErrorCodeEnum.PARAM_ERROR, "Pre-initiation not found: " + preId);
        }
        if (!"SUBMITTED".equals(existing.getStatus())) {
            throw new BusinessException(ErrorCodeEnum.PARAM_ERROR, "Only SUBMITTED applications can be approved");
        }
        existing.setStatus(approved ? "APPROVED" : "REJECTED");
        existing.setApproveTime(LocalDateTime.now());
        existing.setUpdateTime(LocalDateTime.now());
        preInitiationMapper.updateById(existing);
        // TODO: trigger workflow / notification based on approval result
    }

    @Override
    public Page<PreInitiation> listByDept(String deptId, String status, int page, int size) {
        Page<PreInitiation> pageObj = new Page<>(page, size);
        LambdaQueryWrapper<PreInitiation> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(PreInitiation::getDeptId, deptId);
        if (status != null && !status.isEmpty()) {
            wrapper.eq(PreInitiation::getStatus, status);
        }
        wrapper.orderByDesc(PreInitiation::getCreateTime);
        return preInitiationMapper.selectPage(pageObj, wrapper);
    }

    @Override
    public PreInitiation getPreInitiation(String preId) {
        PreInitiation result = preInitiationMapper.selectById(preId);
        if (result == null) {
            throw new BusinessException(ErrorCodeEnum.PARAM_ERROR, "Pre-initiation not found: " + preId);
        }
        return result;
    }
}
