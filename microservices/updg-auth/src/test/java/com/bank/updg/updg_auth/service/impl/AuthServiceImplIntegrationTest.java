package com.bank.updg.updg_auth.service.impl;

import com.bank.updg.common.exception.BusinessException;
import com.bank.updg.updg_auth.model.dto.LoginRequest;
import com.bank.updg.updg_auth.model.vo.LoginResponse;
import com.bank.updg.updg_auth.mapper.UserMapper;
import com.bank.updg.updg_auth.service.PasswordPolicyService;
import org.apache.ibatis.builder.xml.XMLMapperBuilder;
import org.apache.ibatis.datasource.pooled.PooledDataSource;
import org.apache.ibatis.mapping.Environment;
import org.apache.ibatis.session.Configuration;
import org.apache.ibatis.session.SqlSession;
import org.apache.ibatis.session.SqlSessionFactory;
import org.apache.ibatis.session.SqlSessionFactoryBuilder;
import org.apache.ibatis.transaction.jdbc.JdbcTransactionFactory;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.testcontainers.containers.MySQLContainer;
import org.testcontainers.junit.jupiter.Container;
import org.testcontainers.junit.jupiter.Testcontainers;

import java.lang.reflect.Field;
import java.sql.Connection;
import java.sql.Statement;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;

/**
 * Integration test for AuthServiceImpl with real MySQL.
 * Tests login, register, and token flows end-to-end.
 */
@Testcontainers
class AuthServiceImplIntegrationTest {

    @Container
    static MySQLContainer<?> mysql = new MySQLContainer<>("mysql:8.0")
            .withDatabaseName("updg_auth_test")
            .withUsername("test")
            .withPassword("test");

    private SqlSession sqlSession;
    private UserMapper userMapper;
    private AuthServiceImpl authService;

    @BeforeEach
    void setUp() throws Exception {
        PooledDataSource dataSource = new PooledDataSource(
                mysql.getJdbcUrl(),
                mysql.getUsername(),
                mysql.getPassword(),
                "com.mysql.cj.jdbc.Driver"
        );

        Configuration config = new Configuration();
        config.setEnvironment(new Environment(
                "test",
                new JdbcTransactionFactory(),
                dataSource
        ));

        // Register mapper
        config.addMapper(UserMapper.class);
        config.addMapper(com.bank.updg.updg_auth.mapper.LoginAttemptMapper.class);

        SqlSessionFactory sqlSessionFactory = new SqlSessionFactoryBuilder().build(config);
        sqlSession = sqlSessionFactory.openSession();

        // Create tables
        try (Connection conn = sqlSessionFactory.getConfiguration()
                .getEnvironment().getDataSource().getConnection()) {
            Statement stmt = conn.createStatement();
            stmt.execute("""
                CREATE TABLE pm_sys_user (
                    user_id VARCHAR(64) PRIMARY KEY,
                    username VARCHAR(50) NOT NULL UNIQUE,
                    password VARCHAR(100) NOT NULL,
                    name VARCHAR(100),
                    dept_id VARCHAR(64),
                    email VARCHAR(100),
                    phone VARCHAR(20),
                    status INT DEFAULT 1,
                    password_changed_at TIMESTAMP,
                    create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    update_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """);
            stmt.execute("""
                CREATE TABLE pm_login_attempt (
                    attempt_id VARCHAR(64) PRIMARY KEY,
                    user_id VARCHAR(64),
                    username VARCHAR(50),
                    ip_address VARCHAR(50),
                    success INT DEFAULT 0,
                    failure_reason VARCHAR(200),
                    attempt_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """);
        }

        userMapper = sqlSession.getMapper(UserMapper.class);
        var loginAttemptMapper = sqlSession.getMapper(com.bank.updg.updg_auth.mapper.LoginAttemptMapper.class);

        PasswordPolicyService passwordPolicyService =
                new PasswordPolicyServiceImpl(loginAttemptMapper, userMapper);

        authService = new AuthServiceImpl(passwordPolicyService, userMapper);

        // Inject JWT config via reflection
        setField(authService, "jwtSecret", "test-secret-key-for-integration-tests-must-be-32-chars");
        setField(authService, "jwtExpiration", 3600000L);
        authService.init();
    }

    @AfterEach
    void tearDown() {
        if (sqlSession != null) {
            sqlSession.close();
        }
    }

    @Test
    @DisplayName("register + login - full flow works")
    void registerAndLogin_fullFlow_works() throws Exception {
        // Register
        LoginResponse registerResp = authService.register("testuser", "Str0ng!Pass#2026", "Test User");
        assertThat(registerResp.getToken()).isNotBlank();

        sqlSession.commit();

        // Login
        LoginRequest req = new LoginRequest();
        req.setUsername("testuser");
        req.setPassword("Str0ng!Pass#2026");

        LoginResponse loginResp = authService.login(req);

        assertThat(loginResp.getToken()).isNotBlank();
        assertThat(loginResp.getUserInfo().getName()).isEqualTo("Test User");
    }

    @Test
    @DisplayName("login - wrong password throws")
    void login_wrongPassword_throws() throws Exception {
        authService.register("user2", "Str0ng!Pass#2026", "User Two");
        sqlSession.commit();

        LoginRequest req = new LoginRequest();
        req.setUsername("user2");
        req.setPassword("WrongPass123!@#");

        assertThatThrownBy(() -> authService.login(req))
                .isInstanceOf(BusinessException.class);
    }

    @Test
    @DisplayName("login - nonexistent user throws")
    void login_nonexistentUser_throws() {
        LoginRequest req = new LoginRequest();
        req.setUsername("nobody");
        req.setPassword("Str0ng!Pass#2026");

        assertThatThrownBy(() -> authService.login(req))
                .isInstanceOf(BusinessException.class);
    }

    @Test
    @DisplayName("register - duplicate username throws")
    void register_duplicateUsername_throws() throws Exception {
        authService.register("dupuser", "Str0ng!Pass#2026", "First");
        sqlSession.commit();

        assertThatThrownBy(() -> authService.register("dupuser", "An0ther!Pass#2026", "Second"))
                .isInstanceOf(BusinessException.class);
    }

    @Test
    @DisplayName("register - weak password throws")
    void register_weakPassword_throws() {
        assertThatThrownBy(() -> authService.register("newuser", "weak", "New User"))
                .isInstanceOf(BusinessException.class);
    }

    @Test
    @DisplayName("refresh token - valid refresh returns new token")
    void refreshToken_validToken_returnsNewToken() throws Exception {
        authService.register("refreshtest", "Str0ng!Pass#2026", "Refresh Test");
        sqlSession.commit();

        LoginRequest req = new LoginRequest();
        req.setUsername("refreshtest");
        req.setPassword("Str0ng!Pass#2026");

        LoginResponse loginResp = authService.login(req);
        LoginResponse refreshResp = authService.refreshToken(loginResp.getRefreshToken());

        assertThat(refreshResp.getToken()).isNotBlank();
        assertThat(refreshResp.getToken()).isNotEqualTo(loginResp.getToken());
    }

    private void setField(Object target, String fieldName, Object value) throws Exception {
        Field field = target.getClass().getDeclaredField(fieldName);
        field.setAccessible(true);
        field.set(target, value);
    }
}
