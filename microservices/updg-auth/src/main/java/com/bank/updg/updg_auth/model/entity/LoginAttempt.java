package com.bank.updg.updg_auth.model.entity;

import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;

/**
 * Login attempt tracking entity.
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
@TableName("pm_login_attempt")
public class LoginAttempt {

    @TableId
    private String attemptId;

    private String userId;

    private String username;

    private String ipAddress;

    private LocalDateTime attemptTime;

    private Integer success;

    private String failureReason;

    /** Convenience method */
    public boolean isSuccess() {
        return success != null && success == 1;
    }
}
