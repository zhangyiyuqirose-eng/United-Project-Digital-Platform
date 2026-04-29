package com.bank.updg.updg_project;

import org.mybatis.spring.annotation.MapperScan;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication
@MapperScan("com.bank.updg.updg_project.mapper")
public class UpdgProjectApplication {
    public static void main(String[] args) {
        SpringApplication.run(UpdgProjectApplication.class, args);
    }
}
