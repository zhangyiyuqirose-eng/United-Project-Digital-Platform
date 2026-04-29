package com.bank.updg.common.interceptor;

import com.bank.updg.common.util.LogUtil;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import org.springframework.web.servlet.HandlerInterceptor;

/**
 * TraceId 拦截器 - 为每个请求注入唯一 traceId
 */
public class TraceIdInterceptor implements HandlerInterceptor {

    private static final String TRACE_ID_HEADER = "X-Trace-Id";

    @Override
    public boolean preHandle(HttpServletRequest request, HttpServletResponse response,
                             Object handler) {
        // 优先使用请求头传入的 traceId（链路追踪场景）
        String traceId = request.getHeader(TRACE_ID_HEADER);
        if (traceId == null || traceId.isEmpty()) {
            traceId = LogUtil.initTraceId();
        } else {
            LogUtil.initTraceId();
        }
        // 将 traceId 返回给调用方
        response.setHeader(TRACE_ID_HEADER, traceId);
        return true;
    }

    @Override
    public void afterCompletion(HttpServletRequest request, HttpServletResponse response,
                                Object handler, Exception ex) {
        LogUtil.clearTraceId();
    }
}
