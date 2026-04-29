package com.bank.updg.updg_report;

import org.mybatis.spring.annotation.MapperScan;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication
@MapperScan("com.bank.updg.updg_report.mapper")
public class UpdgReportApplication {
    public static void main(String[] args) {
        SpringApplication.run(UpdgReportApplication.class, args);
    }
}
