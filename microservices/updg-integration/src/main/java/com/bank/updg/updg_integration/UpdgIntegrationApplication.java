package com.bank.updg.updg_integration;

import org.mybatis.spring.annotation.MapperScan;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication
@MapperScan("com.bank.updg.updg_integration.mapper")
public class UpdgIntegrationApplication {
    public static void main(String[] args) {
        SpringApplication.run(UpdgIntegrationApplication.class, args);
    }
}
