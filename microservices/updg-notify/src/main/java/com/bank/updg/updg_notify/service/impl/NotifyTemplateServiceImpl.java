package com.bank.updg.updg_notify.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import com.bank.updg.updg_notify.mapper.NotifyTemplateMapper;
import com.bank.updg.updg_notify.model.entity.NotifyTemplate;
import com.bank.updg.updg_notify.service.NotifyTemplateService;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
import java.util.List;
import java.util.UUID;

/**
 * F-1409: Notify template service implementation.
 */
@Service
public class NotifyTemplateServiceImpl extends ServiceImpl<NotifyTemplateMapper, NotifyTemplate>
        implements NotifyTemplateService {

    @Override
    public NotifyTemplate createTemplate(NotifyTemplate template) {
        template.setTemplateId(UUID.randomUUID().toString().replace("-", ""));
        if (template.getIsActive() == null) {
            template.setIsActive("Y");
        }
        template.setCreateTime(LocalDateTime.now());
        template.setUpdateTime(LocalDateTime.now());
        save(template);
        return template;
    }

    @Override
    public NotifyTemplate updateTemplate(NotifyTemplate template) {
        template.setUpdateTime(LocalDateTime.now());
        updateById(template);
        return template;
    }

    @Override
    public List<NotifyTemplate> getByChannel(String channel) {
        LambdaQueryWrapper<NotifyTemplate> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(NotifyTemplate::getChannel, channel.toUpperCase());
        return list(wrapper);
    }

    @Override
    public List<NotifyTemplate> getActiveTemplates() {
        LambdaQueryWrapper<NotifyTemplate> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(NotifyTemplate::getIsActive, "Y");
        return list(wrapper);
    }

    @Override
    public void activateTemplate(String templateId) {
        NotifyTemplate template = getById(templateId);
        if (template != null) {
            template.setIsActive("Y");
            template.setUpdateTime(LocalDateTime.now());
            updateById(template);
        }
    }

    @Override
    public void deactivateTemplate(String templateId) {
        NotifyTemplate template = getById(templateId);
        if (template != null) {
            template.setIsActive("N");
            template.setUpdateTime(LocalDateTime.now());
            updateById(template);
        }
    }
}