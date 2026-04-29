package com.bank.updg.updg_auth.model.vo;

import lombok.Builder;
import lombok.Data;

import java.util.List;

@Data
@Builder
public class LoginResponse {
    private String token;
    private String refreshToken;
    private UserInfoVO userInfo;

    @Data
    @Builder
    public static class UserInfoVO {
        private String userId;
        private String name;
        private List<String> roleIds;
    }
}
