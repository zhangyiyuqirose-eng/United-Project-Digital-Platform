package com.bank.updg.updg_gateway.filter;

import lombok.extern.slf4j.Slf4j;
import org.springframework.cloud.gateway.filter.GatewayFilterChain;
import org.springframework.cloud.gateway.filter.GlobalFilter;
import org.springframework.core.Ordered;
import org.springframework.http.HttpStatus;
import org.springframework.http.server.reactive.ServerHttpRequest;
import org.springframework.stereotype.Component;
import org.springframework.util.StringUtils;
import org.springframework.web.server.ServerWebExchange;
import reactor.core.publisher.Mono;

import java.time.Duration;
import java.time.Instant;

/**
 * Anti-replay attack filter.
 * Requires X-Timestamp and X-Nonce headers; rejects requests older than 5 minutes.
 */
@Slf4j
@Component
public class AntiReplayFilter implements GlobalFilter, Ordered {

    private static final long MAX_AGE_SECONDS = 300;

    @Override
    public Mono<Void> filter(ServerWebExchange exchange, GatewayFilterChain chain) {
        ServerHttpRequest request = exchange.getRequest();
        String timestamp = request.getHeaders().getFirst("X-Timestamp");
        String nonce = request.getHeaders().getFirst("X-Nonce");

        // Allow internal / non-sensitive endpoints without replay protection
        String path = request.getPath().value();
        if (path.startsWith("/actuator") || path.startsWith("/health")) {
            return chain.filter(exchange);
        }

        if (!StringUtils.hasText(timestamp) || !StringUtils.hasText(nonce)) {
            log.warn("Missing anti-replay headers: path={}", path);
            exchange.getResponse().setStatusCode(HttpStatus.BAD_REQUEST);
            return exchange.getResponse().setComplete();
        }

        try {
            Instant reqTime = Instant.parse(timestamp);
            long age = Duration.between(reqTime, Instant.now()).abs().getSeconds();
            if (age > MAX_AGE_SECONDS) {
                log.warn("Replay request expired: age={}s, path={}", age, path);
                exchange.getResponse().setStatusCode(HttpStatus.BAD_REQUEST);
                return exchange.getResponse().setComplete();
            }
        } catch (Exception e) {
            log.warn("Invalid X-Timestamp format: {}", timestamp);
            exchange.getResponse().setStatusCode(HttpStatus.BAD_REQUEST);
            return exchange.getResponse().setComplete();
        }

        // TODO: store nonce in Redis with TTL for deduplication

        return chain.filter(exchange);
    }

    @Override
    public int getOrder() {
        return -200;
    }
}
