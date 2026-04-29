package com.bank.updg.common.mq;

import lombok.extern.slf4j.Slf4j;

/**
 * RocketMQ 消费者抽象基类
 * 各服务继承此类实现具体消费逻辑
 */
@Slf4j
public abstract class AbstractRocketMQConsumer {

    /**
     * 处理消息
     *
     * @param topic   主题
     * @param message 消息体
     * @return 是否消费成功
     */
    public boolean consume(String topic, String message) {
        try {
            log.info("MQ consume: topic={}, message={}", topic, message);
            return doConsume(topic, message);
        } catch (Exception e) {
            log.error("MQ consume error: topic={}", topic, e);
            return false;
        }
    }

    /**
     * 子类实现具体消费逻辑
     */
    protected abstract boolean doConsume(String topic, String message);
}
