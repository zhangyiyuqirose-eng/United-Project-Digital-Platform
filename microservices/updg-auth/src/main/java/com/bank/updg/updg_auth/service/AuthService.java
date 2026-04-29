package com.bank.updg.updg_auth.service;

import com.bank.updg.updg_auth.model.dto.LoginRequest;
import com.bank.updg.updg_auth.model.vo.LoginResponse;

public interface AuthService {

    LoginResponse login(LoginRequest request);

    LoginResponse refreshToken(String refreshToken);

    void logout(String token);

    LoginResponse ssoCallback(String ticket);

    /**
     * Register a new user with password policy validation.
     * Password is hashed with SM3+salt before storage.
     */
    LoginResponse register(String username, String password, String name);
}
