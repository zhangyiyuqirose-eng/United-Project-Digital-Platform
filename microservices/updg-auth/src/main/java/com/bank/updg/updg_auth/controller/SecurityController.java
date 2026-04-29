package com.bank.updg.updg_auth.controller;

import com.bank.updg.common.model.ApiResponse;
import com.bank.updg.updg_auth.service.PasswordPolicyService;
import com.bank.updg.updg_auth.mapper.UserMapper;
import com.bank.updg.updg_auth.model.entity.User;
import com.bank.updg.updg_auth.util.PasswordUtil;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Map;

/**
 * Security management endpoints for password policy and account lockout.
 */
@RestController
@RequestMapping("/api/auth/security")
@RequiredArgsConstructor
public class SecurityController {

    private final PasswordPolicyService passwordPolicyService;
    private final UserMapper userMapper;

    /**
     * Get current password policy configuration.
     */
    @GetMapping("/policy")
    public ApiResponse<Map<String, Object>> getPasswordPolicy() {
        Map<String, Object> policy = Map.of(
                "minLength", 12,
                "requireUppercase", true,
                "requireLowercase", true,
                "requireDigit", true,
                "requireSpecialChar", true,
                "expiryDays", 90,
                "maxFailedAttempts", 5,
                "lockoutDurationMinutes", 30
        );
        return ApiResponse.success(policy);
    }

    /**
     * Change user password. Requires old password verification.
     */
    @PostMapping("/{userId}/change-password")
    public ApiResponse<Void> changePassword(
            @PathVariable String userId,
            @RequestBody Map<String, String> request) {
        String oldPassword = request.get("oldPassword");
        String newPassword = request.get("newPassword");

        if (oldPassword == null || newPassword == null) {
            return ApiResponse.error(com.bank.updg.common.model.enums.ErrorCodeEnum.PARAM_ERROR,
                    "oldPassword and newPassword are required");
        }

        User user = userMapper.selectById(userId);
        if (user == null) {
            return ApiResponse.error(com.bank.updg.common.model.enums.ErrorCodeEnum.PARAM_ERROR,
                    "User not found");
        }

        if (!PasswordUtil.verifyPassword(oldPassword, user.getPassword())) {
            return ApiResponse.error(com.bank.updg.common.model.enums.ErrorCodeEnum.PARAM_ERROR,
                    "Old password is incorrect");
        }

        List<String> violations = passwordPolicyService.validatePassword(newPassword);
        if (!violations.isEmpty()) {
            return ApiResponse.error(com.bank.updg.common.model.enums.ErrorCodeEnum.PARAM_ERROR,
                    String.join("; ", violations));
        }

        user.setPassword(PasswordUtil.hashPassword(newPassword));
        user.setPasswordChangedAt(LocalDateTime.now());
        userMapper.updateById(user);

        return ApiResponse.success();
    }

    /**
     * Check if a user account is locked.
     */
    @GetMapping("/{userId}/lock-status")
    public ApiResponse<Map<String, Object>> getLockStatus(@PathVariable String userId) {
        boolean locked = passwordPolicyService.checkLockStatus(userId);
        boolean expired = passwordPolicyService.checkPasswordExpiry(userId);

        Map<String, Object> status = Map.of(
                "userId", userId,
                "locked", locked,
                "passwordExpired", expired
        );
        return ApiResponse.success(status);
    }

    /**
     * Unlock a user account (admin only).
     */
    @PostMapping("/{userId}/unlock")
    public ApiResponse<Void> unlockAccount(@PathVariable String userId) {
        // TODO: Verify admin role via @RequiresPermission
        passwordPolicyService.unlockAccount(userId);
        return ApiResponse.success();
    }
}
