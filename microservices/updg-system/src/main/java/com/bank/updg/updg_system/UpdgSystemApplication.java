package com.bank.updg.updg_system;

import org.mybatis.spring.annotation.MapperScan;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication
@MapperScan("com.bank.updg.updg_system.mapper")
public class UpdgSystemApplication {
    public static void main(String[] args) {
        SpringApplication.run(UpdgSystemApplication.class, args);
    }
}
