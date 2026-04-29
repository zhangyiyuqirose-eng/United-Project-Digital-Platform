#!/usr/bin/env bash
# Prepare and start all microservices for local testing
# Each service gets a unique port and H2 database

BASE_DIR="/e/公司事务/部门工作/2026数字员工/一站式项目数字化运营管理平台/united-project-digital-platform"
MVN="$BASE_DIR/apache-maven-3.9.6/bin/mvn"
LOG_DIR="$BASE_DIR/logs"

mkdir -p "$LOG_DIR"

# Service port assignments
declare -A PORTS
PORTS[updg-auth]=8083
PORTS[updg-system]=8082
PORTS[updg-project]=8084
PORTS[updg-cost]=8085
PORTS[updg-timesheet]=8086
PORTS[updg-resource]=8087
PORTS[updg-knowledge]=8088
PORTS[updg-workflow]=8089
PORTS[updg-ai]=8090
PORTS[updg-notify]=8091
PORTS[updg-integration]=8092
PORTS[updg-gateway]=8080

echo "============================================"
echo "  Starting Microservices"
echo "  $(date '+%Y-%m-%d %H:%M:%S')"
echo "============================================"

for svc in "${!PORTS[@]}"; do
  port=${PORTS[$svc]}
  svc_dir="$BASE_DIR/microservices/$svc"

  if [ ! -d "$svc_dir" ]; then
    echo "[SKIP] $svc - directory not found"
    continue
  fi

  # Check if already running
  existing=$(netstat -ano 2>/dev/null | grep ":$port " | grep LISTENING | head -1 | awk '{print $5}')
  if [ -n "$existing" ]; then
    echo "[RUNNING] $svc (port $port, PID $existing)"
    continue
  fi

  echo "[START] $svc on port $port..."

  # Override port via environment
  (
    cd "$BASE_DIR" && \
    SERVER_PORT=$port $MVN spring-boot:run \
      -pl "microservices/$svc" \
      -Dspring-boot.run.profiles=dev \
      -Dspring-boot.run.arguments="--server.port=$port" \
      > "$LOG_DIR/$svc.log" 2>&1 &
  )

  echo "  -> PID: $! (log: $LOG_DIR/$svc.log)"
done

echo ""
echo "Waiting for services to start..."
sleep 15

echo ""
echo "============================================"
echo "  Service Status"
echo "============================================"
for svc in "${!PORTS[@]}"; do
  port=${PORTS[$svc]}
  http_code=$(curl -s -o /dev/null -w "%{http_code}" "http://localhost:$port/" 2>/dev/null || echo "000")
  if [ "$http_code" != "000" ]; then
    echo "  [UP] $svc (port $port) - HTTP $http_code"
  else
    echo "  [DOWN] $svc (port $port) - not responding"
  fi
done

echo ""
echo "Done."
