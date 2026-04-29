package com.bank.updg.updg_knowledge;

import org.mybatis.spring.annotation.MapperScan;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication
@MapperScan("com.bank.updg.updg_knowledge.mapper")
public class UpdgKnowledgeApplication {
    public static void main(String[] args) {
        SpringApplication.run(UpdgKnowledgeApplication.class, args);
    }
}
