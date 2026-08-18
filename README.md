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
├── api_objects/          API端点常量和业务服务对象
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

## 常用命令速查

| 目标 | 命令 |
| --- | --- |
| SauceDemo全部用例 | `./scripts/runners/run_test_suite.sh --demo saucedemo` |
| SauceDemo正常回归 | `./scripts/runners/run_test_suite.sh --demo saucedemo --tests cart,checkout,inventory,login,navigation` |
| httpbin API测试 | `./scripts/runners/run_test_suite.sh --demo httpbin` |
| 框架单元测试 | `./scripts/test_env.sh python -m pytest -c config/pytest.ini -m unit cases/unit` |
| 只收集不执行 | `./scripts/test_env.sh python -m pytest -c config/pytest.ini --collect-only cases` |
| 静态检查 | `./scripts/test_env.sh python tools/static_check.py` |

默认统一入口会清理对应类型的旧Allure原始数据，然后执行测试并启动报告服务。只想验证代码、不启动报告时增加 `--no-report`。

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
- `page_objects/web_ui/demoProject/elements/page_login_elements.py`
- `page_objects/web_ui/demoProject/pages/page_login.py`
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
./scripts/test_env.sh python -m scripts.runners.run_api_test \
  -e test \
  -d cases/api/demoProject \
  -k search
```

执行 httpbin API 示例的全部8条用例：

```bash
./scripts/test_env.sh python -m pytest \
  -c config/pytest.ini \
  -v -s \
  --alluredir=output/api/report_data \
  cases/api/httpbin
```

只执行认证相关用例：

```bash
./scripts/test_env.sh python -m pytest \
  -c config/pytest.ini \
  -v \
  -k basic_auth \
  cases/api/httpbin
```

httpbin 默认地址配置在 `config/httpbin/api_httpbin_test.conf`。临时切换兼容服务时可以使用环境变量，无需修改配置文件：

```bash
HTTPBIN_BASE_URL=https://httpbin.org \
  ./scripts/test_env.sh python -m pytest \
  -c config/pytest.ini \
  -v \
  cases/api/httpbin
```

如果公开的 `httpbin.org` 临时返回502、503或504，用例会标记为跳过并明确显示环境不可用。也可以临时使用兼容服务验证框架能力：

```bash
HTTPBIN_BASE_URL=https://httpbingo.org \
  ./scripts/test_env.sh python -m pytest \
  -c config/pytest.ini \
  -v \
  cases/api/httpbin
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

### 统一测试入口

统一入口支持选择demo、测试用例以及是否生成报告。默认执行全部SauceDemo用例，并使用9527端口生成中文报告：

```bash
./scripts/runners/run_test_suite.sh
```

报告地址：<http://127.0.0.1:9527/>

查看所有参数：

```bash
./scripts/runners/run_test_suite.sh --help
```

选择demo：

```bash
./scripts/runners/run_test_suite.sh --demo saucedemo
./scripts/runners/run_test_suite.sh --demo httpbin
./scripts/runners/run_test_suite.sh --demo demoproject
./scripts/runners/run_test_suite.sh --demo web_ui
./scripts/runners/run_test_suite.sh --demo web_ui/demoProject
./scripts/runners/run_test_suite.sh --demo api/httpbin
```

`--demo` 可以传别名，也可以传 `cases` 下的相对目录。新增demo时，只需创建 `cases/web_ui/<new_demo>/` 或 `cases/api/<new_demo>/`，再传对应相对目录，不需要修改运行框架。

Web UI报告默认使用9527端口，API报告默认使用9080端口。执行httpbin并生成API报告：

```bash
./scripts/runners/run_test_suite.sh --demo httpbin
```

公开服务不可用时临时切换兼容地址：

```bash
HTTPBIN_BASE_URL=https://httpbingo.org \
  ./scripts/runners/run_test_suite.sh --demo httpbin
```

`--demo saucedemo`、`--demo web_ui/demoProject` 和 `--demo web_ui` 都会按照pytest默认规则收集 `test_*.py`，不会单独排除故意失败用例。

选择测试功能或关键字，多个值用逗号分隔：

```bash
./scripts/runners/run_test_suite.sh --demo saucedemo --tests login,checkout
./scripts/runners/run_test_suite.sh --demo saucedemo --tests test_logout_returns_to_login_page
```

当前SauceDemo全部用例的预期结果为14条通过、3条故意失败；命令返回状态码1是预期现象，但报告仍会生成。

如需排除故意失败用例，可明确选择正常功能文件：

```bash
./scripts/runners/run_test_suite.sh \
  --demo saucedemo \
  --tests cart,checkout,inventory,login,navigation
```

只执行测试，不生成报告：

```bash
./scripts/runners/run_test_suite.sh --demo saucedemo --tests inventory --no-report
```

保留已有Allure原始数据，不清理后再执行：

```bash
./scripts/runners/run_test_suite.sh --demo saucedemo --keep-report-data
```

旧的SauceDemo命令仍可使用，但内部已转发到统一入口：

```bash
./scripts/reports/run_saucedemo_report.sh
```

单独清理原始数据或历史HTML报告：

```bash
./scripts/reports/clean_web_ui_report_data.sh
./scripts/reports/clean_web_ui_report_data.sh --all
```

### 其他测试类型报告

```bash
./scripts/test_env.sh python -m scripts.reports.generate_api_test_report -p 9080
./scripts/test_env.sh python -m scripts.reports.generate_web_ui_test_report \
  --chrome_port 9527
./scripts/test_env.sh python -m scripts.reports.generate_app_ui_test_report \
  --start_port 9084
```

报告命令会读取 `config/report.conf`，并将生成日志写入 `logs/`。

### Web UI扩展规范

新增页面时，只需按页面对象模型新增文件：

```text
page_objects/web_ui/<demo>/elements/page_<page>_elements.py
page_objects/web_ui/<demo>/pages/page_<page>.py
cases/web_ui/<demo>/test_<demo>_<feature>.py
test_data/web_ui/<demo>/<feature>_test_data.py
```

页面元素定位放在 `elements`，页面操作封装放在 `pages`，测试数据放在 `test_data`，测试用例只负责组合业务步骤和断言。新增测试文件使用 `test_*.py` 命名后，统一入口会自动收集，无需修改框架代码。

例如新增用户资料页面：

```text
page_objects/web_ui/demoProject/elements/page_profile_elements.py
page_objects/web_ui/demoProject/pages/page_profile.py
test_data/web_ui/demoProject/profile_test_data.py
cases/web_ui/demoProject/test_saucedemo_profile.py
```

### API扩展规范

API测试采用与页面对象相同的分层思路：

```text
api_objects/<demo>/endpoints/endpoint_<module>.py
api_objects/<demo>/services/service_<module>.py
test_data/api/<demo>/<module>_test_data.py
cases/api/<demo>/conftest.py
cases/api/<demo>/api/test_<demo>_<module>.py
cases/api/<demo>/scenarios/test_<demo>_<scenario>.py
```

- `endpoints`：只维护接口路径、必要的HTTP方法等不变定义。
- `services`：封装单接口请求以及同一业务模块的复用调用。
- `test_data`：维护请求输入、账号数据和预期结果；敏感数据通过环境变量读取。
- `conftest.py`：统一提供客户端、鉴权和服务fixture。
- `api`：验证单接口参数、状态码、响应结构和异常分支。
- `scenarios`：组合登录、创建、查询、删除等跨接口业务流程。

新增接口模块后，pytest会自动收集 `test_*.py`，不需要修改公共客户端或测试运行器。例如：

```bash
./scripts/runners/run_test_suite.sh \
  --demo api/<demo> \
  --tests <module>
```

## 实际项目接入前必读

当前仓库包含公开网站和历史模块示例，可以作为新项目骨架，但不能直接把演示配置、演示账号和跳过策略原样用于生产项目。接入真实业务前应完成环境隔离、测试数据清理、密钥管理和发布门禁配置。

### 已知风险与规避方式

建议处理顺序：先解决生产安全、密钥和测试数据清理问题；再解决配置缓存、共享Session和并发隔离；最后处理报告、日志、IDE配置和版本升级等工程体验问题。

| 风险 | 当前表现和可能影响 | 实际项目规避方式 |
| --- | --- | --- |
| 配置对象使用单例缓存 | 同一Python进程切换环境后，可能继续使用第一次加载的URL或浏览器配置 | 一个测试进程只运行一个环境；切换环境后重新启动pytest进程；新项目优先使用fixture注入配置，不继续增加全局单例 |
| API客户端共享Session | session级fixture会共享Cookie和请求头，一个用例可能污染后续用例 | 无状态接口可使用session级客户端；登录态、权限和租户场景使用function级客户端，或在用例结束后明确重置Header和Cookie |
| 并发测试数据冲突 | 多个worker使用相同账号、订单号或数据库记录时可能互相覆盖 | 测试数据增加运行批次ID和worker ID；每个用例创建独立数据；结束后通过fixture、事务回滚或清理接口释放数据 |
| 公共测试环境不稳定 | 网络抖动、限流或服务503会导致与代码无关的失败 | 对公共演示服务可以跳过并说明原因；对公司测试、预发布环境不可直接跳过，应将环境不可用单独上报并阻止发布 |
| 重试掩盖真实缺陷 | 不恰当重试可能让偶发失败看起来通过，POST重试还可能重复创建数据 | 仅对连接失败和明确幂等的GET请求重试；POST、支付、下单等操作除非带幂等键，否则禁止自动重试；报告中保留首次失败记录 |
| UI并发和共享配置 | 旧Web运行器会动态修改 `current_browser`，多个作业同时运行可能互相覆盖 | 同一工作目录不要同时启动多个修改配置的Web任务；CI使用独立工作目录；后续逐步改为环境变量或fixture传递浏览器类型 |
| UI定位和等待不稳定 | 使用易变化的CSS层级、固定睡眠或动画元素会产生偶发失败 | 优先使用 `data-test`、稳定ID和显式等待；不要使用固定 `sleep`；页面跳转、弹窗和异步加载必须封装等待条件 |
| 敏感信息泄漏 | 真实账号、密码、Token或云密钥可能进入代码、日志和Allure附件 | 仓库只保存字段结构和公开演示值；真实密钥通过环境变量或CI Secret提供；提交前检查暂存差异；不要把生产响应原文长期保存 |
| 测试报告混入旧数据 | 使用 `--keep-report-data` 会把多次执行结果合并，出现重复或过期用例 | 日常回归保持默认清理；只有明确需要聚合多进程结果时使用该参数；不同测试类型使用独立报告目录 |
| Allure端口和残留进程 | 上一次报告服务未停止时可能出现端口占用 | 优先使用统一入口自动处理本项目启动的Allure进程；其他程序占用端口时使用 `--port` 指定新端口，不要随意终止未知进程 |
| 生成文件进入Git | `.gitignore` 只能忽略未跟踪文件，历史上已跟踪的日志仍会持续显示修改 | 提交前确认 `git status`；不要暂存 `logs/`、`output/`、缓存和下载文件；已跟踪日志应由仓库维护者确认后从Git索引移除 |
| VS Code配置未共享 | `.vscode` 当前被忽略，新成员拉取后不会自动得到本地测试配置 | README作为统一配置来源；每位开发者本地创建 `.vscode/settings.json`；如果团队决定共享，再调整 `.gitignore` 并只提交无个人路径的配置 |
| 版本升级造成不兼容 | Selenium、浏览器、Allure、Appium或pytest大版本升级可能改变行为 | 使用已验证版本；依赖升级单独提交；先运行单元测试、API冒烟和Web冒烟，再更新团队基线版本 |
| 在生产环境执行破坏性测试 | 创建、删除、压力和故障演练可能影响真实用户与数据 | 默认只允许test或staging；production必须使用只读账号和独立marker；压力、删除、支付、消息发送等操作需要单独授权和保护开关 |

### 推荐的真实项目目录

以下示例使用 `my_project`，项目名应使用 `snake_case`：

```text
config/my_project/
├── api_test.conf
├── api_staging.conf
└── web_ui.conf

api_objects/my_project/
├── endpoints/
└── services/

page_objects/web_ui/my_project/
├── components/
├── elements/
└── pages/

test_data/
├── api/my_project/
└── web_ui/my_project/

cases/
├── api/my_project/
│   ├── api/
│   └── scenarios/
└── web_ui/my_project/
```

不要复制 `demoProject` 的单例客户端作为新项目起点。API项目优先使用通用 `base/api/api_client.py`，页面和接口业务能力分别放入 `page_objects` 与 `api_objects`。

### 推荐接入步骤

1. 明确测试环境、基础URL、认证方式、数据库和依赖服务，不使用生产环境作为默认值。
2. 为新项目创建独立配置目录，真实密码和Token只定义环境变量名称，不写具体值。
3. 先实现一个健康检查和一个核心业务冒烟用例，确认网络、权限、报告和清理链路可用。
4. 按端点、Service、测试数据、fixture、用例的顺序扩展，不在测试方法中直接拼接URL或创建底层客户端。
5. 为创建、更新、删除场景设计数据回收方案，并验证用例失败时也能执行清理。
6. 补充正常、异常、边界、权限和重复提交场景，重要API增加状态码、JSON Schema与响应时间断言。
7. UI用例优先覆盖真实用户核心流程，公共导航栏、弹窗、表格等放入 `components`，不要在多个页面重复定位。
8. 本地验证通过后再接入CI，先运行框架单元测试和冒烟测试，再逐步增加完整回归与性能任务。

### 环境与密钥管理

建议一个命令只运行一个环境，并使用环境变量覆盖敏感配置：

```bash
MY_PROJECT_BASE_URL=https://api-test.example.com \
MY_PROJECT_USERNAME=test_user \
MY_PROJECT_PASSWORD='从本地密钥或CI Secret读取' \
  ./scripts/runners/run_test_suite.sh \
  --demo api/my_project \
  --no-report
```

测试代码应在缺少必要密钥时快速失败并显示缺少的变量名，但不能输出变量值。禁止在以下位置保存真实密钥：

- `test_data/`
- `config/*.conf`
- README命令示例
- Allure附件
- `logs/`
- Git提交信息

### 测试数据生命周期

真实项目应保证每条用例都具备完整生命周期：

```text
准备独立数据
→ 执行业务操作
→ 验证接口、页面或数据库结果
→ 无论成功失败都清理数据
```

推荐使用：

- UUID、时间戳或构建号生成唯一用户名、订单号和资源名。
- pytest fixture的 `yield` 在测试结束后执行清理。
- 数据库测试优先使用事务并在结束后回滚。
- 无法立即删除的数据增加固定前缀，定时任务只清理测试前缀数据。
- 不让用例依赖其他用例先执行，也不依赖固定执行顺序。

### 并发执行注意事项

- `pytest-xdist` 使用独立进程，每个worker仍应创建自己的客户端和测试数据。
- `requests.Session` 包含可变Cookie和Header，不要在线程之间共享同一个实例。
- Web UI每个worker必须使用独立浏览器会话、下载目录和账号。
- 同一账号不应同时执行修改个人资料、购物车、订单等有状态场景。
- 首次接入先以单worker验证稳定性，再逐步提高并发数。

### 推荐CI分层

当前仓库没有默认启用GitHub Actions工作流，接入CI时建议分层执行：

| 阶段 | 建议内容 | 失败处理 |
| --- | --- | --- |
| 每次提交 | 静态检查、框架单元测试、API冒烟 | 阻止合并 |
| 合并主分支 | 核心API和Web UI回归 | 阻止发布 |
| 每晚定时 | 全量浏览器、跨接口场景、数据一致性 | 创建缺陷并通知负责人 |
| 发布前 | staging端到端、权限、兼容性 | 不通过则禁止发布 |
| 独立性能任务 | Locust或JMeter压测 | 不与功能测试共用环境和数据 |

建议门禁命令：

```bash
./scripts/test_env.sh python tools/static_check.py
./scripts/test_env.sh python -m pytest -c config/pytest.ini -m unit cases/unit
./scripts/test_env.sh python -m pytest -c config/pytest.ini cases/api/my_project
```

故意失败的 `failure_demo` 用例只用于报告展示，不能加入发布门禁的通过率统计。

### 发布前检查清单

- [ ] 默认环境不是生产环境。
- [ ] 账号、密码、Token和云密钥未进入Git差异。
- [ ] 测试数据具备唯一标识和失败清理方案。
- [ ] 正常、异常、边界和权限场景已覆盖。
- [ ] 外部依赖不可用不会被误判为业务断言失败。
- [ ] 生产或预发布环境不可用不会被静默跳过。
- [ ] 并发用例没有共享账号、Cookie、Header和下载目录。
- [ ] Allure报告没有混入旧结果和敏感数据。
- [ ] `logs/`、`output/`、缓存和本地配置没有被暂存。
- [ ] 静态检查、单元测试和核心冒烟测试通过。

### 进一步优化方向

- 在 `page_objects/**/components/` 中封装导航栏、弹窗、表格等跨页面组件。
- 在 `workflows/` 中封装跨页面或跨接口流程，避免测试用例重复业务步骤。
- 使用 `pytest.mark.parametrize` 维护等价类、边界值和异常数据，减少重复用例代码。
- 通过环境变量和本地忽略配置管理账号、密码和Token，仓库只保存数据结构与演示值。
- 在失败钩子中自动保存截图、页面源码、请求与响应，并作为Allure附件输出。
- 将环境配置对象从全局单例逐步改为fixture注入，便于并行执行多个环境且避免配置缓存串用。
- 为页面对象、服务对象和测试数据增加类型标注，并在提交前增加lint和类型检查。

### 已启用的测试质量能力

- `HttpResponseResult.json()`：统一解析JSON响应。
- `assert_status_code()`：输出预期状态码、实际状态码和请求URL。
- `assert_response_time()`：为重要接口设置响应时间上限。
- `assert_json_schema()`：使用JSON Schema校验响应字段和类型。
- API请求结束后记录状态码、请求地址和响应耗时。
- 测试失败时自动将HTTP请求与响应附加到Allure报告。
- Authorization、Cookie、密码、Token等敏感信息会自动脱敏。
- `api`、`unit`、`failure_demo` marker用于分类选择测试。

只执行框架公共能力单元测试：

```bash
./scripts/test_env.sh python -m pytest \
  -c config/pytest.ini \
  -v \
  -m unit \
  cases/unit
```

只执行故意失败的报告演示用例：

```bash
./scripts/runners/run_test_suite.sh \
  --demo saucedemo \
  --tests failure
```

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
- 页面元素使用 `page_<page>_elements.py`，页面操作使用 `page_<page>.py`。
- API端点使用 `endpoint_<module>.py`，API服务使用 `service_<module>.py`。
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
