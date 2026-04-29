package com.bank.updg.common.model;

import com.bank.updg.common.model.enums.ErrorCodeEnum;
import lombok.Data;

import java.io.Serializable;

/**
 * 统一 API 响应体
 */
@Data
public class ApiResponse<T> implements Serializable {

    private String code;
    private String message;
    private T data;
    private long timestamp;

    public static <T> ApiResponse<T> success(T data) {
        ApiResponse<T> resp = new ApiResponse<>();
        resp.setCode(ErrorCodeEnum.SUCCESS.getCode());
        resp.setMessage(ErrorCodeEnum.SUCCESS.getMessage());
        resp.setData(data);
        resp.setTimestamp(System.currentTimeMillis());
        return resp;
    }

    public static <T> ApiResponse<T> success() {
        return success(null);
    }

    public static <T> ApiResponse<T> error(ErrorCodeEnum errorCode) {
        ApiResponse<T> resp = new ApiResponse<>();
        resp.setCode(errorCode.getCode());
        resp.setMessage(errorCode.getMessage());
        resp.setData(null);
        resp.setTimestamp(System.currentTimeMillis());
        return resp;
    }

    public static <T> ApiResponse<T> error(ErrorCodeEnum errorCode, String message) {
        ApiResponse<T> resp = new ApiResponse<>();
        resp.setCode(errorCode.getCode());
        resp.setMessage(message);
        resp.setData(null);
        resp.setTimestamp(System.currentTimeMillis());
        return resp;
    }

    public static <T> ApiResponse<T> error(String code, String message) {
        ApiResponse<T> resp = new ApiResponse<>();
        resp.setCode(code);
        resp.setMessage(message);
        resp.setData(null);
        resp.setTimestamp(System.currentTimeMillis());
        return resp;
    }
}
