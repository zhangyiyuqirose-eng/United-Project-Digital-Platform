@echo off
REM UPDG Platform - Local Startup Script
REM Starts all microservices using H2 in-memory database

set BASE_DIR=E:\公司事务\部门工作\2026数字员工\一站式项目数字化运营管理平台\pmo-digital-platform
set MVN=%BASE_DIR%\apache-maven-3.9.6\bin\mvn.cmd
set LOG_DIR=%BASE_DIR%\logs

if not exist "%LOG_DIR%" mkdir "%LOG_DIR%"

echo ============================================
echo   UPDG Platform - Starting Microservices
echo   %date% %time%
echo ============================================
echo.

REM First, rebuild common module with new config
echo [PREP] Rebuilding common module...
cd /d "%BASE_DIR%"
call "%MVN%" compile -pl microservices/common -am -DskipTests -q

echo.
echo [INFO] Starting services with H2 in-memory database...
echo.

REM Service definitions: name, port
set SERVICES=updg-gateway:8080 updg-auth:8081 updg-system:8082 updg-project:8083 updg-cost:8087 updg-timesheet:8086 updg-resource:8085 updg-business:8094 updg-knowledge:8088 updg-workflow:8084 updg-ai:8089 updg-report:8092 updg-notify:8091 updg-integration:8090 updg-file:8096 updg-audit:8093 updg-quality:8095

for %%s in (%SERVICES%) do (
    for /f "tokens=1,2 delims=:" %%a in ("%%s") do (
        set SVC_NAME=%%a
        set SVC_PORT=%%b

        echo [START] !SVC_NAME! on port !SVC_PORT!...

        start /b cmd /c "cd /d "%BASE_DIR%" && call "%MVN%" spring-boot:run -pl microservices/!SVC_NAME! -Dspring-boot.run.profiles=local -Dspring-boot.run.arguments="--server.port=!SVC_PORT!" > "%LOG_DIR%\!SVC_NAME!.log" 2>&1"
    )
)

echo.
echo [INFO] Waiting 30 seconds for services to initialize...
timeout /t 30 /nobreak > nul

echo.
echo ============================================
echo   Service Health Check
echo ============================================

for %%s in (%SERVICES%) do (
    for /f "tokens=1,2 delims=:" %%a in ("%%s") do (
        set SVC_NAME=%%a
        set SVC_PORT=%%b

        REM Check if port is listening
        netstat -an | findstr ":!SVC_PORT! " | findstr "LISTENING" > nul
        if !errorlevel! equ 0 (
            echo [UP] !SVC_NAME! (port !SVC_PORT!)
        ) else (
            echo [DOWN] !SVC_NAME! (port !SVC_PORT!) - not responding
        )
    )
)

echo.
echo ============================================
echo   Access Points
echo ============================================
echo   Gateway:     http://localhost:8080
echo   H2 Console:  http://localhost:8080/h2-console (JDBC URL: jdbc:h2:mem:updg)
echo   Auth API:    http://localhost:8081
echo   System API:  http://localhost:8082
echo   Project API: http://localhost:8083
echo ============================================
echo.
echo Logs are in: %LOG_DIR%
echo.

REM Also start frontend
echo [FRONTEND] Starting Vue frontend...
cd /d "%BASE_DIR%\frontend"
start /b cmd /c "npm run dev > "%LOG_DIR%\frontend.log" 2>&1"

echo.
echo Press Ctrl+C to stop all services (they run in background)
echo Check logs in: %LOG_DIR%
pause