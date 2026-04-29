package com.bank.updg.updg_workflow;

import org.mybatis.spring.annotation.MapperScan;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication
@MapperScan("com.bank.updg.updg_workflow.mapper")
public class UpdgWorkflowApplication {
    public static void main(String[] args) {
        SpringApplication.run(UpdgWorkflowApplication.class, args);
    }
}
