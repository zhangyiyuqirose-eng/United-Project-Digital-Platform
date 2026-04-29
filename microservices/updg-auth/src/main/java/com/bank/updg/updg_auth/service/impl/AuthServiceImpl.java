package com.bank.updg.updg_auth.service.impl;

import cn.hutool.crypto.SmUtil;
import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.bank.updg.common.exception.BusinessException;
import com.bank.updg.common.model.enums.ErrorCodeEnum;
import com.bank.updg.common.security.JwtUtil;
import com.bank.updg.updg_auth.model.dto.LoginRequest;
import com.bank.updg.updg_auth.model.entity.User;
import com.bank.updg.updg_auth.mapper.UserMapper;
import com.bank.updg.updg_auth.model.vo.LoginResponse;
import com.bank.updg.updg_auth.service.AuthService;
import com.bank.updg.updg_auth.service.PasswordPolicyService;
import com.bank.updg.updg_auth.util.PasswordUtil;
import jakarta.annotation.PostConstruct;
import lombok.RequiredArgsConstructor;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.Map;
import java.time.LocalDateTime;

@Service
@RequiredArgsConstructor
public class AuthServiceImpl implements AuthService {

    @Value("${jwt.secret:united-project-digital-platform-secret-key-must-be-at-least-32-bytes}")
    private String jwtSecret;

    @Value("${jwt.expiration:86400000}")
    private long jwtExpiration;

    private final PasswordPolicyService passwordPolicyService;
    private final UserMapper userMapper;

    private JwtUtil jwtUtil;

    @PostConstruct
    public void init() {
        this.jwtUtil = new JwtUtil(jwtSecret, jwtExpiration);
    }

    @Override
    public LoginResponse login(LoginRequest request) {
        String username = request.getUsername();
        String password = request.getPassword();

        // Check account lock status
        if (passwordPolicyService.checkLockStatus(username)) {
            throw new BusinessException(ErrorCodeEnum.FORBIDDEN, "Account locked due to too many failed login attempts");
        }

        // Load user from DB
        User user = userMapper.selectOne(new LambdaQueryWrapper<User>()
                .eq(User::getUsername, username));
        if (user == null) {
            passwordPolicyService.recordFailedAttempt(username, "unknown");
            throw new BusinessException(ErrorCodeEnum.LOGIN_FAILED, "用户不存在");
        }

        // Check account status
        if (user.getStatus() != null && user.getStatus() == 0) {
            throw new BusinessException(ErrorCodeEnum.FORBIDDEN, "账号已禁用");
        }

        // Verify password
        if (!PasswordUtil.verifyPassword(password, user.getPassword())) {
            passwordPolicyService.recordFailedAttempt(username, "unknown");
            throw new BusinessException(ErrorCodeEnum.LOGIN_FAILED, "密码错误");
        }

        // Record successful login
        passwordPolicyService.recordSuccessfulLogin(username, "unknown");

        Map<String, Object> claims = Map.of("role", "admin");
        String token = jwtUtil.generateToken(user.getUserId(), claims);
        String refreshToken = jwtUtil.generateToken(user.getUserId(), Map.of("type", "refresh"));

        return LoginResponse.builder()
                .token(token)
                .refreshToken(refreshToken)
                .userInfo(LoginResponse.UserInfoVO.builder()
                        .userId(user.getUserId())
                        .name(user.getName())
                        .roleIds(List.of("1"))
                        .build())
                .build();
    }

    @Override
    public LoginResponse refreshToken(String refreshToken) {
        if (!jwtUtil.isTokenValid(refreshToken)) {
            throw new BusinessException(ErrorCodeEnum.TOKEN_EXPIRED);
        }
        String userId = jwtUtil.getUserId(refreshToken);
        String newToken = jwtUtil.generateToken(userId, Map.of("role", "admin"));
        return LoginResponse.builder()
                .token(newToken)
                .refreshToken(refreshToken)
                .build();
    }

    @Override
    public void logout(String token) {
        // TODO: Add token to Redis blacklist
    }

    @Override
    public LoginResponse ssoCallback(String ticket) {
        // TODO: Validate SSO ticket via SsoAdapter
        throw new BusinessException(ErrorCodeEnum.SSO_ERROR, "SSO 暂未接入");
    }

    @Override
    public LoginResponse register(String username, String password, String name) {
        // Validate password against policy
        List<String> violations = passwordPolicyService.validatePassword(password);
        if (!violations.isEmpty()) {
            throw new BusinessException(ErrorCodeEnum.PARAM_ERROR, String.join("; ", violations));
        }

        // Check username uniqueness
        User existing = userMapper.selectOne(new LambdaQueryWrapper<User>()
                .eq(User::getUsername, username));
        if (existing != null) {
            throw new BusinessException(ErrorCodeEnum.PARAM_ERROR, "用户名已存在");
        }

        // Hash password with SM3 + salt
        String hashedPassword = PasswordUtil.hashPassword(password);

        // Save user to DB
        User newUser = new User();
        newUser.setUserId(java.util.UUID.randomUUID().toString().replace("-", ""));
        newUser.setUsername(username);
        newUser.setPassword(hashedPassword);
        newUser.setName(name);
        newUser.setStatus(1);
        newUser.setPasswordChangedAt(LocalDateTime.now());
        userMapper.insert(newUser);

        Map<String, Object> claims = Map.of("role", "user");
        String token = jwtUtil.generateToken(newUser.getUserId(), claims);
        String refreshToken = jwtUtil.generateToken(newUser.getUserId(), Map.of("type", "refresh"));

        return LoginResponse.builder()
                .token(token)
                .refreshToken(refreshToken)
                .userInfo(LoginResponse.UserInfoVO.builder()
                        .userId(newUser.getUserId())
                        .name(name)
                        .roleIds(List.of())
                        .build())
                .build();
    }
}
