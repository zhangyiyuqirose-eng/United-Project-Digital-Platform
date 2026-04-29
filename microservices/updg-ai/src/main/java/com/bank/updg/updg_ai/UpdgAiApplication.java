package com.bank.updg.updg_ai;

import org.mybatis.spring.annotation.MapperScan;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication
@MapperScan("com.bank.updg.updg_ai.mapper")
public class UpdgAiApplication {
    public static void main(String[] args) {
        SpringApplication.run(UpdgAiApplication.class, args);
    }
}
