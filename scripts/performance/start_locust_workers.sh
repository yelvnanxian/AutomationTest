# 作用：批量启动Locust工作节点并连接指定的主节点。

set -eu

if [ "$#" -lt 2 ]; then
    echo "用法: $0 <locustfile> <master_host> [worker_count]"
    exit 1
fi

PROJECT_ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/../.." && pwd)
WORKER_COUNT=${3:-8}
INDEX=0

while [ "$INDEX" -lt "$WORKER_COUNT" ]; do
    "$PROJECT_ROOT/scripts/test_env.sh" locust -f "$1" --worker --master-host "$2" &
    INDEX=$((INDEX + 1))
done

wait
