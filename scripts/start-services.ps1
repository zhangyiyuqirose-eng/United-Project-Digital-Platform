# UPDG Platform - Start All Services
$baseDir = 'E:\公司事务\部门工作\2026数字员工\一站式项目数字化运营管理平台\pmo-digital-platform'
$mvn = "$baseDir\apache-maven-3.9.6\bin\mvn.cmd"

$services = @{
    'updg-system' = 8082
    'updg-project' = 8083
    'updg-workflow' = 8084
    'updg-resource' = 8085
    'updg-timesheet' = 8086
    'updg-cost' = 8087
    'updg-knowledge' = 8088
    'updg-ai' = 8089
    'updg-integration' = 8090
    'updg-notify' = 8091
    'updg-report' = 8092
    'updg-audit' = 8093
    'updg-business' = 8094
    'updg-quality' = 8095
    'updg-file' = 8096
}

foreach ($service in $services.Keys) {
    $port = $services[$service]
    Write-Host "Starting $service on port $port..."

    $cmd = "cd /d $baseDir && $mvn spring-boot:run -pl microservices/$service -Dspring-boot.run.profiles=local '-Dspring-boot.run.arguments=--server.port=$port'"

    Start-Process -FilePath 'cmd.exe' -ArgumentList '/c', $cmd -WindowStyle Minimized
}

Write-Host "All services starting..."
Write-Host "Gateway: 8080, Auth: 8081 (already running)"