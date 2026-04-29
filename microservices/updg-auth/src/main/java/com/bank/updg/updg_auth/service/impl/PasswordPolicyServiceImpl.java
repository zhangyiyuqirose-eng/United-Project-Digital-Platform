package com.bank.updg.updg_auth.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.bank.updg.updg_auth.mapper.LoginAttemptMapper;
import com.bank.updg.updg_auth.model.entity.LoginAttempt;
import com.bank.updg.updg_auth.service.PasswordPolicyService;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.List;

/**
 * Password policy service implementation.
 *
 * Rules:
 * - Minimum 12 characters
 * - Must contain uppercase, lowercase, digit, and special character
 * - Password expires after 90 days
 * - Account locks after 5 consecutive failed attempts
 */
@Service
@RequiredArgsConstructor
public class PasswordPolicyServiceImpl implements PasswordPolicyService {

    private static final int MIN_LENGTH = 12;
    private static final int MAX_FAILED_ATTEMPTS = 5;
    private static final int PASSWORD_EXPIRY_DAYS = 90;

    private final LoginAttemptMapper loginAttemptMapper;

    /** Query user entity to check password expiry */
    private com.bank.updg.updg_auth.mapper.UserMapper userMapper;

    public PasswordPolicyServiceImpl(LoginAttemptMapper loginAttemptMapper,
                                     com.bank.updg.updg_auth.mapper.UserMapper userMapper) {
        this.loginAttemptMapper = loginAttemptMapper;
        this.userMapper = userMapper;
    }

    @Override
    public List<String> validatePassword(String password) {
        List<String> violations = new ArrayList<>();

        if (password == null || password.length() < MIN_LENGTH) {
            violations.add("Password must be at least " + MIN_LENGTH + " characters");
        }

        if (password != null && !password.matches(".*[A-Z].*")) {
            violations.add("Password must contain at least one uppercase letter");
        }

        if (password != null && !password.matches(".*[a-z].*")) {
            violations.add("Password must contain at least one lowercase letter");
        }

        if (password != null && !password.matches(".*\\d.*")) {
            violations.add("Password must contain at least one digit");
        }

        if (password != null && !password.matches(".*[^A-Za-z0-9].*")) {
            violations.add("Password must contain at least one special character");
        }

        return violations;
    }

    @Override
    public boolean checkPasswordExpiry(String userId) {
        com.bank.updg.updg_auth.model.entity.User user = userMapper.selectById(userId);
        if (user == null || user.getPasswordChangedAt() == null) {
            return false;
        }
        LocalDateTime cutoff = LocalDateTime.now().minusDays(PASSWORD_EXPIRY_DAYS);
        return user.getPasswordChangedAt().isBefore(cutoff);
    }

    @Override
    public boolean checkLockStatus(String userId) {
        LambdaQueryWrapper<LoginAttempt> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(LoginAttempt::getUsername, userId)
               .eq(LoginAttempt::getSuccess, 0)
               .orderByDesc(LoginAttempt::getAttemptTime)
               .last("LIMIT " + MAX_FAILED_ATTEMPTS);

        List<LoginAttempt> recentAttempts = loginAttemptMapper.selectList(wrapper);
        if (recentAttempts.size() < MAX_FAILED_ATTEMPTS) {
            return false;
        }

        // Check if all recent attempts are failed and within a reasonable time window
        LocalDateTime cutoff = LocalDateTime.now().minusMinutes(30);
        boolean allFailed = recentAttempts.stream().allMatch(a -> Integer.valueOf(0).equals(a.getSuccess()));
        boolean recent = recentAttempts.stream().allMatch(a -> a.getAttemptTime().isAfter(cutoff));

        return allFailed && recent;
    }

    @Override
    public void recordFailedAttempt(String username, String ipAddress) {
        LoginAttempt attempt = LoginAttempt.builder()
                .attemptId(java.util.UUID.randomUUID().toString().replace("-", ""))
                .username(username)
                .ipAddress(ipAddress)
                .attemptTime(LocalDateTime.now())
                .success(0)
                .build();
        loginAttemptMapper.insert(attempt);
    }

    @Override
    public void recordSuccessfulLogin(String username, String ipAddress) {
        LoginAttempt attempt = LoginAttempt.builder()
                .attemptId(java.util.UUID.randomUUID().toString().replace("-", ""))
                .username(username)
                .ipAddress(ipAddress)
                .attemptTime(LocalDateTime.now())
                .success(1)
                .build();
        loginAttemptMapper.insert(attempt);
    }

    @Override
    public void unlockAccount(String userId) {
        LambdaQueryWrapper<LoginAttempt> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(LoginAttempt::getUsername, userId)
               .eq(LoginAttempt::getSuccess, 0);
        loginAttemptMapper.delete(wrapper);
    }
}
