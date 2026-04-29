package com.bank.updg.updg_notify.service.impl;

import com.bank.updg.common.exception.BusinessException;
import com.bank.updg.common.model.enums.ErrorCodeEnum;
import com.bank.updg.updg_notify.mapper.NotifyMessageMapper;
import com.bank.updg.updg_notify.model.entity.NotifyMessage;
import com.bank.updg.updg_notify.service.NotifyService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
import java.util.List;
import java.util.UUID;

/**
 * Notification service implementation with multi-channel routing.
 *
 * Routes messages based on channel type:
 * - WECHAT: WeChat Work push notification
 * - EMAIL: Email via Spring Mail
 * - SMS: SMS gateway push
 *
 * All messages are persisted to DB regardless of channel.
 */
@Slf4j
@Service
@RequiredArgsConstructor
public class NotifyServiceImpl implements NotifyService {

    private final NotifyMessageMapper notifyMessageMapper;

    @Override
    public void send(NotifyMessage message) {
        if (message.getMessageId() == null) {
            message.setMessageId(UUID.randomUUID().toString().replace("-", ""));
        }
        if (message.getStatus() == null) {
            message.setStatus("PENDING");
        }
        if (message.getCreateTime() == null) {
            message.setCreateTime(LocalDateTime.now());
        }

        // Persist to DB first
        notifyMessageMapper.insert(message);

        // Route by channel type
        try {
            String channel = message.getChannel();
            if (channel == null) {
                throw new BusinessException(ErrorCodeEnum.PARAM_ERROR, "channel is required");
            }

            switch (channel.toUpperCase()) {
                case "WECHAT":
                    sendViaWechat(message);
                    break;
                case "EMAIL":
                    sendViaEmail(message);
                    break;
                case "SMS":
                    sendViaSms(message);
                    break;
                default:
                    throw new BusinessException(ErrorCodeEnum.PARAM_ERROR,
                            "Unsupported channel: " + channel);
            }

            // Update status to SENT
            message.setStatus("SENT");
            message.setSendTime(LocalDateTime.now());
            notifyMessageMapper.updateById(message);

        } catch (BusinessException e) {
            // Update status to FAILED
            message.setStatus("FAILED");
            message.setErrorMsg(e.getMessage());
            notifyMessageMapper.updateById(message);
            throw e;
        }
    }

    @Override
    public void batchSend(List<NotifyMessage> messages) {
        for (NotifyMessage message : messages) {
            try {
                send(message);
            } catch (Exception e) {
                log.error("Failed to send message to {}: {}", message.getReceiver(), e.getMessage());
            }
        }
    }

    @Override
    public List<NotifyMessage> getByReceiver(String receiver) {
        return notifyMessageMapper.selectList(
                new com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper<NotifyMessage>()
                        .eq(NotifyMessage::getReceiver, receiver)
                        .orderByDesc(NotifyMessage::getCreateTime)
        );
    }

    @Override
    public void markAsRead(String messageId) {
        NotifyMessage message = notifyMessageMapper.selectById(messageId);
        if (message == null) {
            throw new BusinessException(ErrorCodeEnum.NOT_FOUND, "Message not found");
        }
        message.setStatus("READ");
        message.setReadTime(LocalDateTime.now());
        notifyMessageMapper.updateById(message);
    }

    // ---- Channel-specific routing methods ----

    /**
     * Send via WeChat Work (企业微信).
     * TODO: Implement actual WeChat push via REST call to WeChat Work API.
     * Requires: app ID, agent ID, access token management.
     */
    private void sendViaWechat(NotifyMessage message) {
        log.info("Sending WeChat notification to {}: {}", message.getReceiver(), message.getTitle());
        // TODO: Call WeChat Work API
        // 1. Get access token from WeChat Work API
        // 2. POST to https://qyapi.weixin.qq.com/cgi-bin/message/send
        // 3. Body: { "touser": receiver, "msgtype": "text", "agentid": agentId,
        //            "text": { "content": message.getContent() } }
    }

    /**
     * Send via Email.
     * TODO: Implement actual email sending using Spring Mail (JavaMailSender).
     * Requires: SMTP configuration, template engine for HTML emails.
     */
    private void sendViaEmail(NotifyMessage message) {
        log.info("Sending Email notification to {}: {}", message.getReceiver(), message.getTitle());
        // TODO: Use JavaMailSender
        // 1. Inject JavaMailSender
        // 2. Create MimeMessage with title and content
        // 3. Set receiver as TO address
        // 4. Send asynchronously via @Async or thread pool
    }

    /**
     * Send via SMS gateway.
     * TODO: Implement actual SMS push via REST call to SMS provider API.
     * Requires: SMS provider credentials, template ID, signature.
     */
    private void sendViaSms(NotifyMessage message) {
        log.info("Sending SMS notification to {}: {}", message.getReceiver(), message.getTitle());
        // TODO: Call SMS provider API
        // 1. Build REST request with receiver phone number and message content
        // 2. Include API credentials and signature
        // 3. POST to SMS provider endpoint
        // 4. Parse response and handle delivery status
    }
}
