package com.bank.updg.updg_gateway.filter;

import io.jsonwebtoken.Claims;
import io.jsonwebtoken.Jwts;
import io.jsonwebtoken.security.Keys;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.cloud.gateway.filter.GatewayFilterChain;
import org.springframework.cloud.gateway.filter.GlobalFilter;
import org.springframework.core.Ordered;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpStatus;
import org.springframework.http.server.reactive.ServerHttpRequest;
import org.springframework.stereotype.Component;
import org.springframework.web.server.ServerWebExchange;
import reactor.core.publisher.Mono;

import java.nio.charset.StandardCharsets;
import javax.crypto.SecretKey;
import java.security.Key;
import java.util.List;

/**
 * Token validation filter for authenticated routes.
 * Validates JWT token format, signature, and expiration.
 */
@Slf4j
@Component
public class TokenFilter implements GlobalFilter, Ordered {

    private static final List<String> WHITE_LIST = List.of(
            "/api/auth/login",
            "/api/auth/refresh",
            "/api/auth/sso/callback",
            "/actuator",
            "/health"
    );

    @Value("${jwt.secret:united-project-digital-platform-secret-key-at-least-256-bits}")
    private String jwtSecret;

    @Override
    public Mono<Void> filter(ServerWebExchange exchange, GatewayFilterChain chain) {
        String path = exchange.getRequest().getPath().value();

        for (String whitePath : WHITE_LIST) {
            if (path.startsWith(whitePath)) {
                return chain.filter(exchange);
            }
        }

        String authHeader = exchange.getRequest().getHeaders().getFirst(HttpHeaders.AUTHORIZATION);
        if (authHeader == null || !authHeader.startsWith("Bearer ")) {
            log.warn("Missing or invalid Authorization header: path={}", path);
            exchange.getResponse().setStatusCode(HttpStatus.UNAUTHORIZED);
            return exchange.getResponse().setComplete();
        }

        String token = authHeader.substring(7);
        if (token.isBlank()) {
            exchange.getResponse().setStatusCode(HttpStatus.UNAUTHORIZED);
            return exchange.getResponse().setComplete();
        }

        try {
            SecretKey key = Keys.hmacShaKeyFor(jwtSecret.getBytes(StandardCharsets.UTF_8));
            Claims claims = Jwts.parser()
                    .verifyWith(key)
                    .build()
                    .parseSignedClaims(token)
                    .getPayload();

            // Extract user info and forward downstream
            String userId = claims.getSubject();
            String roles = claims.get("roles", String.class);
            ServerHttpRequest mutatedRequest = exchange.getRequest().mutate()
                    .header("X-User-Id", userId != null ? userId : "")
                    .header("X-User-Roles", roles != null ? roles : "")
                    .build();
            return chain.filter(exchange.mutate().request(mutatedRequest).build());
        } catch (io.jsonwebtoken.ExpiredJwtException e) {
            log.warn("Expired JWT token: path={}", path);
            exchange.getResponse().setStatusCode(HttpStatus.UNAUTHORIZED);
            return exchange.getResponse().setComplete();
        } catch (Exception e) {
            log.warn("Invalid JWT token: path={}, error={}", path, e.getMessage());
            exchange.getResponse().setStatusCode(HttpStatus.UNAUTHORIZED);
            return exchange.getResponse().setComplete();
        }
    }

    @Override
    public int getOrder() {
        return -100;
    }
}
