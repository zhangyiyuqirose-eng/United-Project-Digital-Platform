package com.bank.updg.updg_auth.util;

import cn.hutool.crypto.SmUtil;
import cn.hutool.core.util.RandomUtil;

/**
 * Password utility using SM3 hashing with salt.
 */
public final class PasswordUtil {

    private static final int SALT_LENGTH = 16;

    private PasswordUtil() {
    }

    /**
     * Hash a plain-text password with a random salt.
     *
     * @return "sm3hash$salt$digest" format string
     */
    public static String hashPassword(String plain) {
        String salt = RandomUtil.randomString(SALT_LENGTH);
        String digest = SmUtil.sm3(plain + salt);
        return "sm3$" + salt + "$" + digest;
    }

    /**
     * Verify a plain-text password against a stored hash.
     *
     * @param plain  plain-text password
     * @param hashed stored hash in "sm3$salt$digest" format
     * @return true if password matches
     */
    public static boolean verifyPassword(String plain, String hashed) {
        if (plain == null || hashed == null) {
            return false;
        }
        String[] parts = hashed.split("\\$");
        if (parts.length != 3 || !"sm3".equals(parts[0])) {
            return false;
        }
        String salt = parts[1];
        String expectedDigest = parts[2];
        String actualDigest = SmUtil.sm3(plain + salt);
        return actualDigest.equals(expectedDigest);
    }
}
