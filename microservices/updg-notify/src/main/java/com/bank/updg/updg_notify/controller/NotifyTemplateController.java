package com.bank.updg.updg_notify.controller;

import com.bank.updg.common.model.ApiResponse;
import com.bank.updg.updg_notify.model.entity.NotifyTemplate;
import com.bank.updg.updg_notify.service.NotifyTemplateService;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

import java.util.List;

/**
 * F-1409: Notify template controller.
 */
@RestController
@RequestMapping("/api/notify/template")
@RequiredArgsConstructor
public class NotifyTemplateController {

    private final NotifyTemplateService notifyTemplateService;

    @PostMapping
    public ApiResponse<NotifyTemplate> create(@RequestBody NotifyTemplate template) {
        return ApiResponse.success(notifyTemplateService.createTemplate(template));
    }

    @GetMapping
    public ApiResponse<List<NotifyTemplate>> listAll() {
        return ApiResponse.success(notifyTemplateService.list());
    }

    @PutMapping("/{id}")
    public ApiResponse<NotifyTemplate> update(@PathVariable String id,
                                              @RequestBody NotifyTemplate template) {
        template.setTemplateId(id);
        return ApiResponse.success(notifyTemplateService.updateTemplate(template));
    }

    @GetMapping("/{id}")
    public ApiResponse<NotifyTemplate> getById(@PathVariable String id) {
        return ApiResponse.success(notifyTemplateService.getById(id));
    }

    @GetMapping("/channel/{channel}")
    public ApiResponse<List<NotifyTemplate>> getByChannel(@PathVariable String channel) {
        return ApiResponse.success(notifyTemplateService.getByChannel(channel));
    }

    @GetMapping("/active")
    public ApiResponse<List<NotifyTemplate>> getActiveTemplates() {
        return ApiResponse.success(notifyTemplateService.getActiveTemplates());
    }

    @PostMapping("/{id}/activate")
    public ApiResponse<Void> activate(@PathVariable String id) {
        notifyTemplateService.activateTemplate(id);
        return ApiResponse.success();
    }

    @PostMapping("/{id}/deactivate")
    public ApiResponse<Void> deactivate(@PathVariable String id) {
        notifyTemplateService.deactivateTemplate(id);
        return ApiResponse.success();
    }

    @DeleteMapping("/{id}")
    public ApiResponse<Void> delete(@PathVariable String id) {
        notifyTemplateService.removeById(id);
        return ApiResponse.success();
    }
}