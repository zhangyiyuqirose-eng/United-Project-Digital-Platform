package com.bank.updg.updg_system.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.bank.updg.common.exception.BusinessException;
import com.bank.updg.common.model.enums.ErrorCodeEnum;
import com.bank.updg.updg_system.mapper.SysAnnouncementMapper;
import com.bank.updg.updg_system.model.entity.SysAnnouncement;
import com.bank.updg.updg_system.service.AnnouncementService;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
import java.util.List;
import java.util.UUID;

@Service
@RequiredArgsConstructor
public class AnnouncementServiceImpl implements AnnouncementService {

    private final SysAnnouncementMapper announcementMapper;

    @Override
    public SysAnnouncement createAnnouncement(SysAnnouncement data) {
        data.setAnnouncementId(UUID.randomUUID().toString().replace("-", ""));
        data.setStatus("DRAFT");
        data.setCreateTime(LocalDateTime.now());
        announcementMapper.insert(data);
        return data;
    }

    @Override
    public void publishAnnouncement(String announcementId) {
        SysAnnouncement existing = announcementMapper.selectById(announcementId);
        if (existing == null) {
            throw new BusinessException(ErrorCodeEnum.PARAM_ERROR, "Announcement not found: " + announcementId);
        }
        if (!"DRAFT".equals(existing.getStatus())) {
            throw new BusinessException(ErrorCodeEnum.PARAM_ERROR, "Only DRAFT announcements can be published");
        }
        existing.setStatus("PUBLISHED");
        existing.setPublishTime(LocalDateTime.now());
        announcementMapper.updateById(existing);
    }

    @Override
    public SysAnnouncement getAnnouncement(String announcementId) {
        SysAnnouncement result = announcementMapper.selectById(announcementId);
        if (result == null) {
            throw new BusinessException(ErrorCodeEnum.PARAM_ERROR, "Announcement not found: " + announcementId);
        }
        return result;
    }

    @Override
    public Page<SysAnnouncement> listAnnouncements(String type, String status, int page, int size) {
        Page<SysAnnouncement> pageObj = new Page<>(page, size);
        LambdaQueryWrapper<SysAnnouncement> wrapper = new LambdaQueryWrapper<>();
        if (type != null && !type.isEmpty()) {
            wrapper.eq(SysAnnouncement::getType, type);
        }
        if (status != null && !status.isEmpty()) {
            wrapper.eq(SysAnnouncement::getStatus, status);
        }
        wrapper.orderByDesc(SysAnnouncement::getCreateTime);
        return announcementMapper.selectPage(pageObj, wrapper);
    }

    @Override
    public List<SysAnnouncement> listActiveAnnouncements() {
        LocalDateTime now = LocalDateTime.now();
        return announcementMapper.selectList(
                new LambdaQueryWrapper<SysAnnouncement>()
                        .eq(SysAnnouncement::getStatus, "PUBLISHED")
                        .and(w -> w.isNull(SysAnnouncement::getExpiryTime)
                                .or()
                                .gt(SysAnnouncement::getExpiryTime, now))
                        .orderByDesc(SysAnnouncement::getPublishTime));
    }

    @Override
    public void deleteAnnouncement(String announcementId) {
        SysAnnouncement existing = announcementMapper.selectById(announcementId);
        if (existing == null) {
            throw new BusinessException(ErrorCodeEnum.PARAM_ERROR, "Announcement not found: " + announcementId);
        }
        announcementMapper.deleteById(announcementId);
    }
}
