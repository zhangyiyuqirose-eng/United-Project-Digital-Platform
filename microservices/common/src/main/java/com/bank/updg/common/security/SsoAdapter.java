package com.bank.updg.common.security;

import java.util.Map;

/**
 * SSO 对接适配接口 - 预留行内 SSO 系统对接
 */
public interface SsoAdapter {

    /**
     * 验证 SSO Ticket
     *
     * @param ticket SSO 回调票据
     * @return 用户信息（userId, name, roleIds）
     */
    Map<String, Object> validateTicket(String ticket);

    /**
     * 构建 SSO 登录 URL
     *
     * @param redirectUri 回调地址
     * @return SSO 登录跳转地址
     */
    String buildSsoLoginUrl(String redirectUri);

    /**
     * SSO 注销
     *
     * @param token 当前 Token
     */
    void logout(String token);
}
