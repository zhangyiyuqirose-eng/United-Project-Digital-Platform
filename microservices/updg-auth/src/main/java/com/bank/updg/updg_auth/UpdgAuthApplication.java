package com.bank.updg.updg_auth;

import org.mybatis.spring.annotation.MapperScan;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication
@MapperScan("com.bank.updg.updg_auth.mapper")
public class UpdgAuthApplication {
    public static void main(String[] args) {
        SpringApplication.run(UpdgAuthApplication.class, args);
    }
}
