package com.bank.updg.common.security;

import java.lang.annotation.*;

/**
 * 权限校验注解
 * 使用方法：@RequiresPermission("project:view")
 */
@Target({ElementType.METHOD, ElementType.TYPE})
@Retention(RetentionPolicy.RUNTIME)
@Documented
public @interface RequiresPermission {

    /**
     * 权限标识
     */
    String value();

    /**
     * 逻辑关系（AND / OR）
     */
    Logical logical() default Logical.OR;
}
