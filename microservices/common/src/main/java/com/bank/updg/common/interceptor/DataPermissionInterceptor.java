package com.bank.updg.common.interceptor;

import com.bank.updg.common.annotation.DataScope;
import com.baomidou.mybatisplus.core.toolkit.PluginUtils;
import com.baomidou.mybatisplus.extension.plugins.inner.InnerInterceptor;
import org.apache.ibatis.executor.Executor;
import org.apache.ibatis.mapping.BoundSql;
import org.apache.ibatis.mapping.MappedStatement;
import org.apache.ibatis.session.ResultHandler;
import org.apache.ibatis.session.RowBounds;

/**
 * MyBatis-Plus InnerInterceptor that adds row-level data permission WHERE clauses
 * based on the current user's department and role.
 *
 * Admin users bypass the filter. Non-admin users get dept_id = current_dept_id
 * appended to their queries for tables annotated with @DataScope.
 */
public class DataPermissionInterceptor implements InnerInterceptor {

    private static final String ADMIN_ROLE = "admin";

    /**
     * ThreadLocal holder for current user context.
     * Should be set by auth filter/interceptor before request processing.
     */
    private static final ThreadLocal<UserContext> USER_CONTEXT = new ThreadLocal<>();

    /**
     * Set the current user context for this thread.
     */
    public static void setUserContext(String userId, String deptId, boolean isAdmin) {
        USER_CONTEXT.set(new UserContext(userId, deptId, isAdmin));
    }

    /**
     * Clear the current user context. Should be called after request completion.
     */
    public static void clearUserContext() {
        USER_CONTEXT.remove();
    }

    /**
     * Get the current user context.
     */
    public static UserContext getUserContext() {
        return USER_CONTEXT.get();
    }

    @Override
    public void beforeQuery(Executor executor, MappedStatement ms, Object parameter,
                            RowBounds rowBounds, ResultHandler resultHandler, BoundSql boundSql) {
        UserContext context = USER_CONTEXT.get();
        if (context == null || context.isAdmin()) {
            return;
        }

        String deptId = context.deptId();
        if (deptId == null || deptId.isBlank()) {
            return;
        }

        Class<?> entityClass = extractEntityClass(ms);
        if (entityClass == null) {
            return;
        }

        DataScope dataScope = entityClass.getAnnotation(DataScope.class);
        if (dataScope == null) {
            return;
        }

        String column = dataScope.deptColumn();
        String originalSql = boundSql.getSql();
        String newSql = appendDeptFilter(originalSql, column, deptId);

        PluginUtils.MPBoundSql mpBs = PluginUtils.mpBoundSql(boundSql);
        mpBs.sql(newSql);
    }

    /**
     * Append dept_id filter to the original SQL using string manipulation.
     * Handles WHERE / ORDER BY / GROUP BY / LIMIT clauses correctly.
     */
    private String appendDeptFilter(String originalSql, String column, String deptId) {
        String lowerSql = originalSql.toLowerCase();

        // Find the position of the last WHERE that is not inside a subquery
        // Simple approach: find "where " after the main SELECT
        int lastWhere = findMainWhere(lowerSql);

        String deptCondition = column + " = '" + deptId + "'";

        if (lastWhere == -1) {
            // No WHERE clause found - check for ORDER BY, GROUP BY, LIMIT
            int orderPos = lowerSql.lastIndexOf("order by");
            int groupPos = lowerSql.lastIndexOf("group by");
            int limitPos = lowerSql.lastIndexOf("limit");

            int insertPos = -1;
            if (orderPos != -1) insertPos = orderPos;
            if (groupPos != -1 && (insertPos == -1 || groupPos < insertPos)) insertPos = groupPos;
            if (limitPos != -1 && (insertPos == -1 || limitPos < insertPos)) insertPos = limitPos;

            if (insertPos != -1) {
                return originalSql.substring(0, insertPos)
                        + " WHERE " + deptCondition + " "
                        + originalSql.substring(insertPos);
            } else {
                return originalSql + " WHERE " + deptCondition;
            }
        } else {
            // Append after WHERE, before ORDER BY / GROUP BY / LIMIT
            int afterWhere = lastWhere + 5; // skip "where"
            String before = originalSql.substring(0, afterWhere);
            String after = originalSql.substring(afterWhere);
            String afterLower = after.toLowerCase();

            int orderPos = afterLower.indexOf("order by");
            int groupPos = afterLower.indexOf("group by");
            int limitPos = afterLower.indexOf("limit");

            int cutPos = after.length();
            if (orderPos != -1) cutPos = Math.min(cutPos, orderPos);
            if (groupPos != -1) cutPos = Math.min(cutPos, groupPos);
            if (limitPos != -1) cutPos = Math.min(cutPos, limitPos);

            String middle = after.substring(0, cutPos).trim();
            String trailing = after.substring(cutPos);

            return before + " " + deptCondition + " AND " + middle + " " + trailing;
        }
    }

    /**
     * Find the position of the WHERE keyword that belongs to the main SELECT,
     * not inside a subquery.
     */
    private int findMainWhere(String lowerSql) {
        int depth = 0;
        int i = 0;
        while (i < lowerSql.length() - 4) {
            char c = lowerSql.charAt(i);
            if (c == '(') {
                depth++;
                i++;
            } else if (c == ')') {
                depth--;
                i++;
            } else if (depth == 0 && lowerSql.startsWith("where ", i)) {
                return i;
            } else {
                i++;
            }
        }
        return -1;
    }

    /**
     * Extract the entity class from MappedStatement.
     */
    private Class<?> extractEntityClass(MappedStatement ms) {
        try {
            String id = ms.getId();
            String mapperClassName = id.substring(0, id.lastIndexOf('.'));
            Class<?> mapperClass = Class.forName(mapperClassName);

            // Try to get the model type from the mapper's generic parameters
            java.lang.reflect.Type[] interfaces = mapperClass.getGenericInterfaces();
            for (java.lang.reflect.Type iface : interfaces) {
                if (iface instanceof java.lang.reflect.ParameterizedType pt) {
                    java.lang.reflect.Type[] args = pt.getActualTypeArguments();
                    if (args.length > 0 && args[0] instanceof Class<?> clazz) {
                        return clazz;
                    }
                }
            }
        } catch (ClassNotFoundException e) {
            // Ignore
        }
        return null;
    }

    /**
     * User context holder for data permission.
     */
    public record UserContext(String userId, String deptId, boolean isAdmin) {
    }
}
