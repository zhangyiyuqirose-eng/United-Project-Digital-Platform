package com.bank.updg.common.exception;

import com.bank.updg.common.model.enums.ErrorCodeEnum;
import lombok.Getter;

/**
 * 业务异常
 */
@Getter
public class BusinessException extends RuntimeException {

    private final ErrorCodeEnum errorCode;

    public BusinessException(ErrorCodeEnum errorCode) {
        super(errorCode.getMessage());
        this.errorCode = errorCode;
    }

    public BusinessException(ErrorCodeEnum errorCode, String message) {
        super(message);
        this.errorCode = errorCode;
    }

    public BusinessException(ErrorCodeEnum errorCode, Throwable cause) {
        super(errorCode.getMessage(), cause);
        this.errorCode = errorCode;
    }
}
