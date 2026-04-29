package com.bank.updg.updg_notify.service;

import com.baomidou.mybatisplus.extension.service.IService;
import com.bank.updg.updg_notify.model.entity.NotifyTemplate;

import java.util.List;

/**
 * F-1409: Notify template service.
 */
public interface NotifyTemplateService extends IService<NotifyTemplate> {

    NotifyTemplate createTemplate(NotifyTemplate template);

    NotifyTemplate updateTemplate(NotifyTemplate template);

    List<NotifyTemplate> getByChannel(String channel);

    List<NotifyTemplate> getActiveTemplates();

    void activateTemplate(String templateId);

    void deactivateTemplate(String templateId);
}