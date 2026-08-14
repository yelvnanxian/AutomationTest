# 作用：启动Locust主节点并加载指定的性能测试文件。

set -eu

if [ "$#" -lt 1 ]; then
    echo "用法: $0 <locustfile>"
    exit 1
fi

PROJECT_ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/../.." && pwd)
exec "$PROJECT_ROOT/scripts/test_env.sh" locust -f "$1" --master
