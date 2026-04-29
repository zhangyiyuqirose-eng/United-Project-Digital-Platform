package com.bank.updg.updg_system.service;

import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.bank.updg.updg_system.model.entity.SysAnnouncement;

import java.util.List;

public interface AnnouncementService {

    SysAnnouncement createAnnouncement(SysAnnouncement data);

    void publishAnnouncement(String announcementId);

    SysAnnouncement getAnnouncement(String announcementId);

    Page<SysAnnouncement> listAnnouncements(String type, String status, int page, int size);

    List<SysAnnouncement> listActiveAnnouncements();

    void deleteAnnouncement(String announcementId);
}
