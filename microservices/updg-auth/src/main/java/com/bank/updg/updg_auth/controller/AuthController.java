package com.bank.updg.updg_auth.controller;

import com.bank.updg.common.model.ApiResponse;
import com.bank.updg.updg_auth.model.dto.LoginRequest;
import com.bank.updg.updg_auth.model.vo.LoginResponse;
import com.bank.updg.updg_auth.service.AuthService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/auth")
@RequiredArgsConstructor
public class AuthController {

    private final AuthService authService;

    @PostMapping("/login")
    public ApiResponse<LoginResponse> login(@Valid @RequestBody LoginRequest request) {
        return ApiResponse.success(authService.login(request));
    }

    @PostMapping("/refresh")
    public ApiResponse<LoginResponse> refresh(@RequestHeader("X-Refresh-Token") String refreshToken) {
        return ApiResponse.success(authService.refreshToken(refreshToken));
    }

    @PostMapping("/logout")
    public ApiResponse<Void> logout(@RequestHeader(value = "Authorization", required = false) String token) {
        if (token != null && token.startsWith("Bearer ")) {
            authService.logout(token.substring(7));
        }
        return ApiResponse.success();
    }

    @GetMapping("/sso/callback")
    public ApiResponse<LoginResponse> ssoCallback(@RequestParam String ticket) {
        return ApiResponse.success(authService.ssoCallback(ticket));
    }
}
