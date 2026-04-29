package com.bank.updg.updg_cost;

import org.mybatis.spring.annotation.MapperScan;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication
@MapperScan("com.bank.updg.updg_cost.mapper")
public class UpdgCostApplication {
    public static void main(String[] args) {
        SpringApplication.run(UpdgCostApplication.class, args);
    }
}
