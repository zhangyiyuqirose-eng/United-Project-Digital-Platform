package com.bank.updg.updg_file;

import org.mybatis.spring.annotation.MapperScan;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication
@MapperScan("com.bank.updg.updg_file.mapper")
public class UpdgFileApplication {
    public static void main(String[] args) {
        SpringApplication.run(UpdgFileApplication.class, args);
    }
}
