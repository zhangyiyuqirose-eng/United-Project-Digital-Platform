package com.bank.updg.common.mq;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.apache.rocketmq.spring.core.RocketMQTemplate;
import org.springframework.messaging.Message;
import org.springframework.messaging.support.MessageBuilder;
import org.springframework.stereotype.Component;

/**
 * RocketMQ 通用生产者封装
 */
@Slf4j
@Component
@RequiredArgsConstructor
public class RocketMQProducer {

    private final RocketMQTemplate rocketMQTemplate;

    /**
     * 发送普通消息
     */
    public void send(String destination, Object payload) {
        rocketMQTemplate.convertAndSend(destination, payload);
        log.info("MQ send: destination={}, payload={}", destination, payload);
    }

    /**
     * 发送延迟消息
     *
     * @param destination 目标 topic
     * @param payload     消息体
     * @param delayLevel  延迟级别（1-18，对应不同时间）
     */
    public void sendDelay(String destination, Object payload, int delayLevel) {
        Message<Object> message = MessageBuilder.withPayload(payload).build();
        rocketMQTemplate.syncSend(destination, message, 3000, delayLevel);
        log.info("MQ delay send: destination={}, delayLevel={}", destination, delayLevel);
    }

    /**
     * 发送事务消息
     */
    public void sendTransaction(String destination, Object payload, Object argument) {
        rocketMQTemplate.sendMessageInTransaction(
                destination,
                MessageBuilder.withPayload(payload).build(),
                argument
        );
        log.info("MQ transaction send: destination={}", destination);
    }
}
