package com.bank.updg.updg_quality;

import org.mybatis.spring.annotation.MapperScan;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication
@MapperScan("com.bank.updg.updg_quality.mapper")
public class UpdgQualityApplication {
    public static void main(String[] args) {
        SpringApplication.run(UpdgQualityApplication.class, args);
    }
}
