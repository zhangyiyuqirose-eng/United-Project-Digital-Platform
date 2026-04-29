package com.bank.updg.common.util;

/**
 * 数据脱敏工具
 */
public class DesensitizationUtil {

    private static final String DEFAULT_MASK = "****";

    /**
     * 身份证脱敏：保留前 6 后 4
     */
    public static String idCard(String idCard) {
        if (idCard == null || idCard.length() < 10) {
            return DEFAULT_MASK;
        }
        return idCard.substring(0, 6) + "********" + idCard.substring(idCard.length() - 4);
    }

    /**
     * 手机号脱敏：保留前 3 后 4
     */
    public static String phone(String phone) {
        if (phone == null || phone.length() < 7) {
            return DEFAULT_MASK;
        }
        return phone.substring(0, 3) + "****" + phone.substring(phone.length() - 4);
    }

    /**
     * 姓名脱敏：保留姓氏，名字用 *
     */
    public static String name(String name) {
        if (name == null || name.isEmpty()) {
            return DEFAULT_MASK;
        }
        if (name.length() == 1) {
            return name;
        }
        return name.charAt(0) + "*".repeat(name.length() - 1);
    }

    /**
     * 邮箱脱敏：保留前 2 和 @ 后域名
     */
    public static String email(String email) {
        if (email == null || !email.contains("@")) {
            return DEFAULT_MASK;
        }
        String[] parts = email.split("@");
        String prefix = parts[0];
        if (prefix.length() <= 2) {
            return "**@" + parts[1];
        }
        return prefix.substring(0, 2) + "****@" + parts[1];
    }

    /**
     * 银行卡脱敏：保留后 4 位
     */
    public static String bankCard(String cardNo) {
        if (cardNo == null || cardNo.length() < 4) {
            return DEFAULT_MASK;
        }
        return "************" + cardNo.substring(cardNo.length() - 4);
    }
}
