package com.bank.updg.common.annotation;

import java.lang.annotation.ElementType;
import java.lang.annotation.Retention;
import java.lang.annotation.RetentionPolicy;
import java.lang.annotation.Target;

/**
 * Data scope annotation for row-level data permission filtering.
 * Place on entity classes to enable automatic dept/user filtering.
 */
@Target(ElementType.TYPE)
@Retention(RetentionPolicy.RUNTIME)
public @interface DataScope {

    /**
     * Department column name for filtering. Defaults to "dept_id".
     */
    String deptColumn() default "dept_id";

    /**
     * User column name for filtering. Defaults to "create_by".
     */
    String userColumn() default "create_by";
}
