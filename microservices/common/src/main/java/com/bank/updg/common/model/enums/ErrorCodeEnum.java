package com.bank.updg.common.model.enums;

import lombok.AllArgsConstructor;
import lombok.Getter;

/**
 * 统一错误码枚举
 */
@Getter
@AllArgsConstructor
public enum ErrorCodeEnum {

    SUCCESS("SUCCESS", "操作成功"),
    SYSTEM_ERROR("SYSTEM_ERROR", "系统内部错误"),
    PARAM_ERROR("PARAM_ERROR", "参数校验失败"),
    UNAUTHORIZED("UNAUTHORIZED", "未授权访问"),
    FORBIDDEN("FORBIDDEN", "权限不足"),
    NOT_FOUND("NOT_FOUND", "资源不存在"),
    DUPLICATE("DUPLICATE", "数据重复"),
    TIMEOUT("TIMEOUT", "请求超时"),
    RATE_LIMIT("RATE_LIMIT", "请求频率超限"),

    // 认证相关
    LOGIN_FAILED("AUTH_LOGIN_FAILED", "登录失败，用户名或密码错误"),
    TOKEN_EXPIRED("AUTH_TOKEN_EXPIRED", "令牌已过期"),
    TOKEN_INVALID("AUTH_TOKEN_INVALID", "令牌无效"),
    CAPTCHA_ERROR("AUTH_CAPTCHA_ERROR", "验证码错误"),
    SSO_ERROR("AUTH_SSO_ERROR", "SSO 认证失败"),

    // 系统管理
    USER_NOT_FOUND("SYS_USER_NOT_FOUND", "用户不存在"),
    USER_DISABLED("SYS_USER_DISABLED", "用户已禁用"),
    ROLE_NOT_FOUND("SYS_ROLE_NOT_FOUND", "角色不存在"),
    DEPT_NOT_FOUND("SYS_DEPT_NOT_FOUND", "部门不存在"),

    // 项目管理
    PROJECT_NOT_FOUND("PROJECT_NOT_FOUND", "项目不存在"),
    PROJECT_STATUS_ERROR("PROJECT_STATUS_ERROR", "项目状态异常"),
    PROJECT_CHANGE_DENIED("PROJECT_CHANGE_DENIED", "项目变更审批未通过"),

    // 资源管理
    STAFF_NOT_FOUND("RESOURCE_STAFF_NOT_FOUND", "外包人员不存在"),
    STAFF_STATUS_ERROR("RESOURCE_STAFF_STATUS_ERROR", "人员状态异常"),
    UNSPENT_HOURS("RESOURCE_UNSPENT_HOURS", "存在未结算工时，无法离场"),

    // 工时管理
    TIMESHEET_OVERFLOW("TIMESHEET_OVERFLOW", "单日工时超过上限（8 小时）"),
    TIMESHEET_NOT_FOUND("TIMESHEET_NOT_FOUND", "工时记录不存在"),

    // 成本管理
    COST_CALCULATE_ERROR("COST_CALCULATE_ERROR", "成本核算异常"),
    SETTLEMENT_ERROR("COST_SETTLEMENT_ERROR", "结算单生成异常"),

    // 工作流
    WORKFLOW_NOT_FOUND("WORKFLOW_NOT_FOUND", "流程实例不存在"),
    TASK_NOT_FOUND("WORKFLOW_TASK_NOT_FOUND", "任务不存在"),
    TASK_ALREADY_DONE("WORKFLOW_TASK_ALREADY_DONE", "任务已处理"),

    // AI 服务
    AI_GENERATE_ERROR("AI_GENERATE_ERROR", "AI 文档生成失败"),
    NLQ_PARSE_ERROR("NLQ_PARSE_ERROR", "自然语言解析失败"),

    // 通知
    NOTIFY_SEND_ERROR("NOTIFY_SEND_ERROR", "消息发送失败"),

    // 文件服务
    FILE_NOT_FOUND("FILE_NOT_FOUND", "文件不存在"),

    // 集成
    INTEGRATION_ERROR("INTEGRATION_ERROR", "外部系统对接失败"),
    INTEGRATION_TIMEOUT("INTEGRATION_TIMEOUT", "外部系统请求超时");

    private final String code;
    private final String message;
}
