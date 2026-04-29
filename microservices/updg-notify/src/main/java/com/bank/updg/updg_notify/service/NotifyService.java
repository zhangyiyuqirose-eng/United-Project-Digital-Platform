package com.bank.updg.updg_notify.service;

import com.bank.updg.updg_notify.model.entity.NotifyMessage;

import java.util.List;

/**
 * Notification service with multi-channel routing.
 */
public interface NotifyService {

    /**
     * Send a notification through the specified channel.
     */
    void send(NotifyMessage message);

    /**
     * Send notifications to multiple receivers.
     */
    void batchSend(List<NotifyMessage> messages);

    /**
     * Get messages for a user.
     */
    List<NotifyMessage> getByReceiver(String receiver);

    /**
     * Mark a message as read.
     */
    void markAsRead(String messageId);
}
