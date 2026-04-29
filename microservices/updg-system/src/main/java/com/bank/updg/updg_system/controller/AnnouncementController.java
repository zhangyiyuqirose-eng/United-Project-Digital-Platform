package com.bank.updg.updg_system.controller;

import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.bank.updg.common.model.ApiResponse;
import com.bank.updg.updg_system.model.entity.SysAnnouncement;
import com.bank.updg.updg_system.service.AnnouncementService;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/system/announcement")
@RequiredArgsConstructor
public class AnnouncementController {

    private final AnnouncementService announcementService;

    @PostMapping
    public ApiResponse<SysAnnouncement> create(@RequestBody SysAnnouncement data) {
        return ApiResponse.success(announcementService.createAnnouncement(data));
    }

    @PutMapping("/{id}/publish")
    public ApiResponse<Void> publish(@PathVariable String id) {
        announcementService.publishAnnouncement(id);
        return ApiResponse.success();
    }

    @GetMapping("/{id}")
    public ApiResponse<SysAnnouncement> getDetail(@PathVariable String id) {
        return ApiResponse.success(announcementService.getAnnouncement(id));
    }

    @GetMapping("/list")
    public ApiResponse<Page<SysAnnouncement>> list(
            @RequestParam(required = false) String type,
            @RequestParam(required = false) String status,
            @RequestParam(defaultValue = "1") int page,
            @RequestParam(defaultValue = "10") int size) {
        return ApiResponse.success(announcementService.listAnnouncements(type, status, page, size));
    }

    @GetMapping("/active")
    public ApiResponse<List<SysAnnouncement>> getActive() {
        return ApiResponse.success(announcementService.listActiveAnnouncements());
    }

    @DeleteMapping("/{id}")
    public ApiResponse<Void> delete(@PathVariable String id) {
        announcementService.deleteAnnouncement(id);
        return ApiResponse.success();
    }
}
