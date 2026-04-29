package com.bank.updg.updg_notify;

import org.mybatis.spring.annotation.MapperScan;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication
@MapperScan("com.bank.updg.updg_notify.mapper")
public class UpdgNotifyApplication {
    public static void main(String[] args) {
        SpringApplication.run(UpdgNotifyApplication.class, args);
    }
}
