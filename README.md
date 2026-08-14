<!-- 作用：说明自动化测试框架的目录结构、环境准备和常用执行方式。 -->

# AutomationTest

AutomationTest 是一个基于 Python 和 pytest 的自动化测试框架，覆盖以下场景：

- API 自动化测试
- Web UI 自动化测试
- App UI 自动化测试
- App Monkey 稳定性测试
- Locust 性能测试
- Allure 测试报告

## 项目结构

```text
AutomationTest/
├── base/                 基础客户端和配置读取层
├── cases/                pytest 测试用例
├── common/               通用客户端与工具模块
├── common_projects/      可复用的项目业务能力
├── config/               pytest、Web、App、报告等配置
├── init/                 测试运行前的初始化逻辑
├── models/               持久化模型和示例数据库
├── packages/             移动端待测安装包
├── page_objects/         Web/App 页面对象
├── pojo/                 配置和传输对象
├── requirements/         分场景依赖和旧环境兼容依赖
├── scripts/
│   ├── runners/          测试运行入口
│   ├── reports/          Allure 报告入口
│   ├── performance/      Locust 主节点和工作节点脚本
│   ├── services/         Selenium 等本地服务脚本
│   └── test_env.sh       项目环境命令包装器
├── test_data/            测试数据
└── tools/                静态检查和维护工具
```

根目录只保留通用项目文件，例如 README、默认依赖入口、Node.js 清单和 Git 配置。

## 推荐环境

当前验证基线：

| 组件 | 推荐版本 |
| --- | --- |
| Python | 3.12.14 |
| pytest | 8.4.2 |
| Selenium Python | 4.47.0 |
| Selenium Server | 4.47.0 |
| Java | 21 LTS |
| Maven | 3.9.16 |
| Allure | 2.45.0 |
| Node.js | 22 LTS |
| Appium | 3.6.0 |

旧版 Python 3.6 依赖保存在 `requirements/legacy.txt`，仅用于维护历史项目，不建议用于新测试。

## 安装依赖

### Web 测试

```bash
python3.12 -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -r requirements.txt
```

`requirements.txt` 默认引用 `requirements/web.txt`。

### Appium 移动端测试

```bash
.venv/bin/python -m pip install -r requirements/mobile.txt
npm ci
```

Appium 驱动按实际平台安装，例如：

```bash
./scripts/test_env.sh appium driver install uiautomator2
./scripts/test_env.sh appium driver install xcuitest
```

### Locust 性能测试

```bash
.venv/bin/python -m pip install -r requirements/performance.txt
```

## 环境命令包装器

macOS 开发环境中建议通过以下脚本执行命令：

```bash
./scripts/test_env.sh python --version
./scripts/test_env.sh pytest --version
./scripts/test_env.sh appium --version
```

脚本会切换到项目根目录，并加载项目的 Python、Java、Node.js 和 Appium 路径。

## Web UI 测试

### 启动 Selenium

在第一个终端执行：

```bash
./scripts/services/start_selenium.sh
```

默认监听 `4444` 端口，可通过 `SELENIUM_PORT` 修改：

```bash
SELENIUM_PORT=5555 ./scripts/services/start_selenium.sh
```

### 执行 SauceDemo 登录测试

在第二个终端执行：

```bash
./scripts/test_env.sh python -m pytest \
  -c config/pytest.ini \
  -v -s \
  --alluredir output/web_ui/chrome/report_data \
  cases/web_ui/demoProject/test_saucedemo_login.py
```

相关文件：

- `cases/web_ui/demoProject/test_saucedemo_login.py`
- `page_objects/web_ui/demoProject/elements/login_page_elements.py`
- `page_objects/web_ui/demoProject/pages/login_page.py`
- `config/demoProject/web_ui_demo_project.conf`

### 使用 Web UI 运行入口

```bash
./scripts/test_env.sh python -m scripts.runners.run_web_ui_test --help
./scripts/test_env.sh python -m scripts.runners.run_web_ui_test -k login
```

## 其他测试入口

### API 测试

```bash
./scripts/test_env.sh python -m scripts.runners.run_api_test --help
./scripts/test_env.sh python -m scripts.runners.run_api_test -e test
```

### App UI 测试

```bash
./scripts/test_env.sh python -m scripts.runners.run_app_ui_test --help
./scripts/test_env.sh python -m scripts.runners.run_app_ui_test \
  --test_type phone \
  --devices_info_file config/demoProject/app_ui_android_devices_info_demo_project.conf
```

### App Monkey 测试

```bash
./scripts/test_env.sh python -m scripts.runners.run_app_ui_monkey_test --help
```

### Locust 性能测试

```bash
./scripts/performance/start_locust_master.sh cases/performance/demoProject/baidu_index/baidu_index.py
./scripts/performance/start_locust_workers.sh \
  cases/performance/demoProject/baidu_index/baidu_index.py \
  127.0.0.1 \
  8
```

## Allure 报告

```bash
./scripts/test_env.sh python -m scripts.reports.generate_api_test_report -p 9080
./scripts/test_env.sh python -m scripts.reports.generate_web_ui_test_report \
  --chrome_port 9082 \
  --firefox_port 9083
./scripts/test_env.sh python -m scripts.reports.generate_app_ui_test_report \
  --start_port 9084
```

报告命令会读取 `config/report.conf`，并将生成日志写入 `logs/`。

## 配置说明

- `config/pytest.ini`：pytest 日志、插件和 marker 配置
- `config/web_ui_config.conf`：Selenium Hub、浏览器和并发数
- `config/app_ui_config.conf`：Appium 和 App UI 公共配置
- `config/report.conf`：Allure 报告端口
- `config/demoProject/`：示例项目环境配置

`demoProject` 是现有示例项目标识，为避免破坏历史配置键和测试数据路径暂时保留；新增项目和新增文件应使用 `snake_case` 命名。

## 开发规范

- Python 文件、函数和变量使用 `snake_case`。
- Python 类使用 `PascalCase`。
- 测试文件使用 `test_<project>_<feature>.py`。
- 测试类以 `Test` 开头，测试方法以 `test_` 开头。
- 页面元素放在 `page_objects/**/elements/`，页面操作放在 `page_objects/**/pages/`。
- 测试入口、报告入口、服务脚本不要放在项目根目录。
- 文件顶部保留一条准确描述用途的模块注释，不维护手写创建时间或最后修改时间。
- 密钥、Token、密码和真实服务器地址通过环境变量或本地忽略配置提供。

## 提交前检查

```bash
./scripts/test_env.sh python tools/static_check.py
./scripts/test_env.sh python -m pip check
git diff --check
```

静态检查会验证 Python 语法、必要目录、报告脚本安全规则、根目录布局和 Python 文件命名。
