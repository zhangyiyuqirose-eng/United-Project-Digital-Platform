package com.bank.updg.common.util;

import cn.hutool.crypto.SmUtil;
import cn.hutool.crypto.digest.DigestUtil;

/**
 * 加密工具（国密算法）
 */
public class CryptoUtil {

    /**
     * SM3 摘要（用于密码哈希）
     */
    public static String sm3Hash(String data) {
        return SmUtil.sm3(data);
    }

    /**
     * SM3 摘要 + 盐值
     */
    public static String sm3HashWithSalt(String data, String salt) {
        return SmUtil.sm3(data + salt);
    }

    /**
     * SHA-256 摘要（兜底）
     */
    public static String sha256(String data) {
        return DigestUtil.sha256Hex(data);
    }
}
