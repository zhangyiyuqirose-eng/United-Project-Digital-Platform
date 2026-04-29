package com.bank.updg.updg_business;

import org.mybatis.spring.annotation.MapperScan;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication
@MapperScan("com.bank.updg.updg_business.mapper")
public class UpdgBusinessApplication {
    public static void main(String[] args) {
        SpringApplication.run(UpdgBusinessApplication.class, args);
    }
}
