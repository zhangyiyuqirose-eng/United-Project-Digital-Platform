package com.bank.updg.updg_resource;

import org.mybatis.spring.annotation.MapperScan;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication
@MapperScan("com.bank.updg.updg_resource.mapper")
public class UpdgResourceApplication {
    public static void main(String[] args) {
        SpringApplication.run(UpdgResourceApplication.class, args);
    }
}
