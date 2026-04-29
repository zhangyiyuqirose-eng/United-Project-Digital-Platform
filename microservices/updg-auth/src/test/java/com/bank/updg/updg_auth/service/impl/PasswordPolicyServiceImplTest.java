package com.bank.updg.updg_auth.service.impl;

import com.bank.updg.updg_auth.mapper.LoginAttemptMapper;
import com.bank.updg.updg_auth.mapper.UserMapper;
import com.bank.updg.updg_auth.model.entity.LoginAttempt;
import com.bank.updg.updg_auth.model.entity.User;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import java.time.LocalDateTime;
import java.util.List;

import static org.assertj.core.api.Assertions.assertThat;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
class PasswordPolicyServiceImplTest {

    @Mock
    private LoginAttemptMapper loginAttemptMapper;

    @Mock
    private UserMapper userMapper;

    private PasswordPolicyServiceImpl service;

    @BeforeEach
    void setUp() {
        service = new PasswordPolicyServiceImpl(loginAttemptMapper, userMapper);
    }

    @Test
    @DisplayName("validatePassword - weak password returns violations")
    void validatePassword_weakPassword_returnsViolations() {
        List<String> violations = service.validatePassword("short");

        assertThat(violations).isNotEmpty();
        assertThat(violations).anyMatch(v -> v.contains("12 characters"));
    }

    @Test
    @DisplayName("validatePassword - strong password returns no violations")
    void validatePassword_strongPassword_noViolations() {
        List<String> violations = service.validatePassword("Str0ng!Pass#2026");

        assertThat(violations).isEmpty();
    }

    @Test
    @DisplayName("validatePassword - null password returns violations")
    void validatePassword_nullPassword_returnsViolations() {
        List<String> violations = service.validatePassword(null);

        assertThat(violations).isNotEmpty();
    }

    @Test
    @DisplayName("validatePassword - missing special char returns violation")
    void validatePassword_noSpecialChar_returnsViolation() {
        List<String> violations = service.validatePassword("StrongPass1234");

        assertThat(violations).anyMatch(v -> v.contains("special character"));
    }

    @Test
    @DisplayName("recordFailedAttempt - persists attempt to DB")
    void recordFailedAttempt_savesAttempt() {
        service.recordFailedAttempt("testuser", "192.168.1.1");

        verify(loginAttemptMapper).insert(any(LoginAttempt.class));
    }

    @Test
    @DisplayName("recordSuccessfulLogin - persists success to DB")
    void recordSuccessfulLogin_savesAttempt() {
        service.recordSuccessfulLogin("testuser", "192.168.1.1");

        verify(loginAttemptMapper).insert(any(LoginAttempt.class));
    }

    @Test
    @DisplayName("checkLockStatus - fewer than 5 failures returns false")
    void checkLockStatus_fewFailures_notLocked() {
        when(loginAttemptMapper.selectList(any())).thenReturn(List.of(
                failedAttempt(1),
                failedAttempt(2),
                failedAttempt(3)
        ));

        assertThat(service.checkLockStatus("testuser")).isFalse();
    }

    @Test
    @DisplayName("checkLockStatus - 5 failures within 30 min returns true")
    void checkLockStatus_manyRecentFailures_locked() {
        LocalDateTime recent = LocalDateTime.now().minusMinutes(5);
        List<LoginAttempt> recentFailures = List.of(
                failedAttemptRecent(recent),
                failedAttemptRecent(recent),
                failedAttemptRecent(recent),
                failedAttemptRecent(recent),
                failedAttemptRecent(recent)
        );
        when(loginAttemptMapper.selectList(any())).thenReturn(recentFailures);

        assertThat(service.checkLockStatus("testuser")).isTrue();
    }

    @Test
    @DisplayName("unlockAccount - deletes failed attempts")
    void unlockAccount_clearsFailures() {
        service.unlockAccount("testuser");

        verify(loginAttemptMapper).delete(argThat(wrapper -> true));
    }

    @Test
    @DisplayName("checkPasswordExpiry - recent password not expired")
    void checkPasswordExpiry_recentPassword_notExpired() {
        User user = new User();
        user.setPasswordChangedAt(LocalDateTime.now().minusDays(30));
        when(userMapper.selectById("user1")).thenReturn(user);

        assertThat(service.checkPasswordExpiry("user1")).isFalse();
    }

    @Test
    @DisplayName("checkPasswordExpiry - old password is expired")
    void checkPasswordExpiry_oldPassword_expired() {
        User user = new User();
        user.setPasswordChangedAt(LocalDateTime.now().minusDays(100));
        when(userMapper.selectById("user1")).thenReturn(user);

        assertThat(service.checkPasswordExpiry("user1")).isTrue();
    }

    @Test
    @DisplayName("checkPasswordExpiry - null user returns false")
    void checkPasswordExpiry_nullUser_notExpired() {
        when(userMapper.selectById("user1")).thenReturn(null);

        assertThat(service.checkPasswordExpiry("user1")).isFalse();
    }

    private LoginAttempt failedAttempt(int i) {
        return LoginAttempt.builder()
                .attemptId(String.valueOf(i))
                .username("testuser")
                .success(0)
                .attemptTime(LocalDateTime.now().minusHours(i))
                .build();
    }

    private LoginAttempt failedAttemptRecent(LocalDateTime time) {
        return LoginAttempt.builder()
                .attemptId(String.valueOf(System.nanoTime()))
                .username("testuser")
                .success(0)
                .attemptTime(time)
                .build();
    }
}
