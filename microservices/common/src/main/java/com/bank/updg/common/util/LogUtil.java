package com.bank.updg.common.util;

import cn.hutool.core.util.StrUtil;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.slf4j.MDC;

import java.util.UUID;

/**
 * 日志工具 - 封装 SLF4J，自动注入 traceId
 */
public class LogUtil {

    private static final String TRACE_ID_KEY = "traceId";

    public static Logger get(Class<?> clazz) {
        return LoggerFactory.getLogger(clazz);
    }

    /**
     * 生成 traceId 并注入 MDC
     */
    public static String initTraceId() {
        String traceId = UUID.randomUUID().toString().replace("-", "");
        MDC.put(TRACE_ID_KEY, traceId);
        return traceId;
    }

    /**
     * 获取当前 traceId
     */
    public static String getTraceId() {
        return MDC.get(TRACE_ID_KEY);
    }

    /**
     * 清除 traceId
     */
    public static void clearTraceId() {
        MDC.remove(TRACE_ID_KEY);
    }

    /**
     * 构建结构化日志前缀
     */
    public static String structured(String module, String operator, String operation) {
        return StrUtil.format("[{}] [module={}] [operator={}] [op={}]",
                getTraceId(), module, operator, operation);
    }
}
