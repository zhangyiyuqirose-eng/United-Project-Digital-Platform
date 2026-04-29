package com.bank.updg.updg_timesheet;

import org.mybatis.spring.annotation.MapperScan;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication
@MapperScan("com.bank.updg.updg_timesheet.mapper")
public class UpdgTimesheetApplication {
    public static void main(String[] args) {
        SpringApplication.run(UpdgTimesheetApplication.class, args);
    }
}
