package com.bank.updg.updg_gateway.filter;

import lombok.extern.slf4j.Slf4j;
import org.springframework.cloud.gateway.filter.GatewayFilterChain;
import org.springframework.cloud.gateway.filter.GlobalFilter;
import org.springframework.core.Ordered;
import org.springframework.http.HttpHeaders;
import org.springframework.http.server.reactive.ServerHttpRequest;
import org.springframework.http.server.reactive.ServerHttpResponse;
import org.springframework.stereotype.Component;
import org.springframework.web.server.ServerWebExchange;
import reactor.core.publisher.Mono;

import java.util.List;

/**
 * XSS filtering for requests passing through the gateway.
 * Strips common XSS patterns from query parameters and headers.
 */
@Slf4j
@Component
public class XssFilter implements GlobalFilter, Ordered {

    private static final String[] XSS_PATTERNS = {
            "<script", "</script>", "javascript:", "onerror=",
            "onload=", "eval(", "document.cookie", "document.write"
    };

    @Override
    public Mono<Void> filter(ServerWebExchange exchange, GatewayFilterChain chain) {
        ServerHttpRequest request = exchange.getRequest();
        HttpHeaders headers = request.getHeaders();

        for (List<String> values : headers.values()) {
            for (String value : values) {
                if (containsXss(value)) {
                    log.warn("XSS attempt blocked: path={}", request.getPath().value());
                    ServerHttpResponse response = exchange.getResponse();
                    response.setStatusCode(org.springframework.http.HttpStatus.BAD_REQUEST);
                    return response.setComplete();
                }
            }
        }

        return chain.filter(exchange);
    }

    private boolean containsXss(String value) {
        if (value == null) {
            return false;
        }
        String lower = value.toLowerCase();
        for (String pattern : XSS_PATTERNS) {
            if (lower.contains(pattern)) {
                return true;
            }
        }
        return false;
    }

    @Override
    public int getOrder() {
        return -150;
    }
}
