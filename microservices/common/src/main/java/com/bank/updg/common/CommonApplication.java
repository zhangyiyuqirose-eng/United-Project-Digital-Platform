package com.bank.updg.common;

import org.mybatis.spring.annotation.MapperScan;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

/**
 * 公共模块启动类
 */
@SpringBootApplication
@MapperScan("com.bank.updg.common.mapper")
public class CommonApplication {
    public static void main(String[] args) {
        SpringApplication.run(CommonApplication.class, args);
    }
}
