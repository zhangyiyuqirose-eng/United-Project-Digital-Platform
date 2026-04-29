# UPDG 一站式项目数字化运营管理平台

> 银行级项目管理平台 | Spring Boot 3.2 + Spring Cloud Alibaba + Vue3

## 项目概述

面向银行 UPDG 的一站式项目数字化运营管理平台，覆盖项目全生命周期管理、人力外包资源池、成本自动核算、AI 辅助文档生成等核心能力。

## 技术栈

| 层级 | 技术选型 |
|------|---------|
| 后端 | Spring Boot 3.2.5, Spring Cloud 2023.0.1, Spring Cloud Alibaba 2023.0.1 |
| ORM | MyBatis-Plus 3.5.7 |
| 数据库 | MySQL 8.0 / 达梦 DM8 |
| 缓存 | Redis |
| 消息 | RocketMQ |
| 流程 | Flowable 7.0.1 |
| 前端 | Vue 3.4, Vite 5.2, Element Plus 2.6, Pinia 2.1 |
| 安全 | Bouncy Castle (SM2/SM3/SM4), JWT |
| 部署 | K8s, Docker |
| 监控 | SkyWalking, Prometheus, Grafana, ELK |

## 微服务清单

| 服务 | 端口 | 说明 |
|------|------|------|
| updg-gateway | 8080 | API 网关 |
| updg-auth | 8081 | 认证中心 |
| updg-system | 8082 | 系统管理 |
| updg-project | 8083 | 项目全生命周期 |
| updg-cost | 8084 | 成本核算 |
| updg-timesheet | 8085 | 工时管理 |
| updg-resource | 8086 | 人力外包资源池 |
| updg-business | 8087 | 商务管理 |
| updg-knowledge | 8088 | 知识管理 |
| updg-workflow | 8089 | 流程引擎 |
| updg-ai | 8090 | PM 数字员工 |
| updg-report | 8091 | 报表服务 |
| updg-notify | 8092 | 通知消息 |
| updg-integration | 8093 | 集成适配 |
| updg-file | 8094 | 文件服务 |
| updg-audit | 8095 | 审计日志 |
| updg-quality | 8096 | 质量管理 |

## 快速开始

### 后端

```bash
# 编译
./mvnw clean package -DskipTests

# 启动单个服务（示例：认证服务）
cd microservices/updg-auth
../../mvnw spring-boot:run
```

### 前端

```bash
cd frontend
npm install
npm run dev
```

## 开发规范

- Java 代码遵循《阿里巴巴 Java 开发手册》
- 前端遵循 Vue 官方规范
- 所有接口返回统一格式 `{code, message, data, timestamp}`
- 敏感数据禁止硬编码
- 单元测试覆盖率 ≥80%

## 许可证

版权所有 © 2026
