package com.bank.updg.updg_auth.service;

import java.util.List;

/**
 * Password policy validation and account lockout service.
 */
public interface PasswordPolicyService {

    /**
     * Validate password against policy rules.
     *
     * @return list of policy violations; empty list means password is valid
     */
    List<String> validatePassword(String password);

    /**
     * Check if the user's password has expired.
     *
     * @return true if password is expired and must be changed
     */
    boolean checkPasswordExpiry(String userId);

    /**
     * Check if the user's account is locked due to failed login attempts.
     *
     * @return true if account is locked
     */
    boolean checkLockStatus(String userId);

    /**
     * Record a failed login attempt.
     */
    void recordFailedAttempt(String username, String ipAddress);

    /**
     * Record a successful login attempt.
     */
    void recordSuccessfulLogin(String username, String ipAddress);

    /**
     * Unlock a user account.
     */
    void unlockAccount(String userId);
}
