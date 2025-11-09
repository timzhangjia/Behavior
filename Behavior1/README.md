# Behavior Framework

基于Playwright和Behave的Python UI和API自动化测试框架，支持BDD行为驱动开发。

## 🚀 特性

- **BDD测试**: 基于Behave框架，支持使用自然语言编写测试用例
- **元素定位**: 支持YAML配置文件管理元素定位信息
- **API测试**: 通用的API请求和断言方法
- **数据驱动**: 支持Excel、YAML、JSON等数据文件读取
- **数据库支持**: 支持MySQL、PostgreSQL、SQLite数据库操作
- **Allure报告**: 集成Allure测试报告功能
- **并行测试**: 支持并行执行测试用例
- **Jenkins集成**: 支持Jenkins CI/CD集成

## 📦 安装

1. 克隆项目或下载源代码
2. 安装依赖：

```bash
pip install -r requirements.txt
```

3. 安装Playwright浏览器：

```bash
playwright install
```

4. 安装Allure命令行工具（用于生成报告）：

```bash
# Windows (使用Scoop)
scoop install allure

# macOS (使用Homebrew)
brew install allure

# Linux
# 下载并解压Allure，添加到PATH
```

## 🎯 快速开始

### 使用Behave编写测试用例

1. 在 `features` 目录下创建 `.feature` 文件：

```gherkin
# language: zh-CN
功能: API测试示例
  作为测试人员
  我想要测试API接口
  以便验证API功能是否正常

  @api @smoke
  场景: 获取单个帖子信息
    当我初始化API客户端，基础URL为"https://jsonplaceholder.typicode.com"
    当我发送"GET"请求到"posts/1"
    那么响应状态码应该是"200"
    那么响应JSON中"id"的值应该是"1"
```

2. 运行测试：

```bash
# 执行所有feature文件
python run.py

# 执行指定feature文件
python run.py -f features/api_example.feature

# 执行指定tag的用例
python run.py -t smoke

# 并行执行测试
python run.py --parallel -w 4

# 生成Allure报告
python run.py --report
```

### 元素定位配置

在 `data/elements` 目录下创建YAML配置文件：

```yaml
# data/elements/common.yaml
login_page:
  username_input: 
    type: "id"
    value: "username"
  password_input:
    type: "id"
    value: "password"
  login_button:
    type: "css"
    value: "button[type='submit']"
```

在测试中使用：

```gherkin
当我打开页面"login_page"，URL为"https://example.com/login"
当我在"username_input"元素中输入"testuser"
当我在"password_input"元素中输入"password"
当我点击"login_button"元素
```

## 🏗️ 框架结构

```
behavior_framework/
├── api/                      # API测试模块
│   ├── client.py            # API客户端
│   ├── request_handler.py   # 通用请求处理器
│   ├── assertions.py        # API断言
│   └── response.py          # 响应处理
├── ui/                       # UI测试模块
│   ├── browser.py           # 浏览器管理
│   ├── page.py              # 页面管理
│   └── element.py           # 元素管理
├── config/                   # 配置管理
│   └── settings.py          # 设置配置
└── utils/                    # 工具模块
    ├── logger.py            # 日志工具
    ├── file_reader.py       # 文件读取工具
    └── database.py          # 数据库工具

features/                     # Behave测试用例目录
├── steps/                   # 步骤定义
│   ├── api_steps.py        # API测试步骤
│   └── ui_steps.py         # UI测试步骤
├── environment.py           # Behave环境配置
└── *.feature               # 测试用例文件

data/                        # 测试数据目录
└── elements/               # 元素定位配置
    └── common.yaml

tests/                       # 示例代码
├── api_example.py          # API测试示例
└── ui_example.py           # UI测试示例
```

## 📝 编写测试用例

### API测试示例

```gherkin
# language: zh-CN
功能: 用户API测试
  场景: 创建用户
    当我初始化API客户端，基础URL为"https://api.example.com"
    当我发送"POST"请求到"users"，请求体为
      """
      {
        "name": "测试用户",
        "email": "test@example.com"
      }
      """
    那么响应状态码应该是"201"
    那么响应JSON中"name"的值应该是"测试用户"
```

### UI测试示例

```gherkin
# language: zh-CN
功能: 登录测试
  场景: 用户登录
    当我打开浏览器
    当我打开页面"login_page"，URL为"https://example.com/login"
    当我在"username_input"元素中输入"testuser"
    当我在"password_input"元素中输入"password123"
    当我点击"login_button"元素
    当我等待页面加载完成
    那么页面URL应该包含"dashboard"
```

## ⚙️ 配置

### 环境变量配置

复制 `env.example` 为 `.env` 文件并修改配置：

```bash
# 浏览器配置
HEADLESS=false
BROWSER_TYPE=chromium
DEFAULT_TIMEOUT=30000

# API配置
API_BASE_URL=https://api.example.com

# 数据库配置
DB_TYPE=mysql
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=password
DB_NAME=testdb

# Jenkins配置
JENKINS_URL=http://jenkins.example.com
JENKINS_USERNAME=admin
JENKINS_API_TOKEN=your_token
```

## 🧪 运行测试

### 使用run.py执行

```bash
# 执行所有测试
python run.py

# 执行指定feature文件
python run.py -f features/api_example.feature

# 执行指定tag的用例
python run.py -t smoke

# 执行多个tag的用例
python run.py -t smoke,api

# 并行执行（4个worker）
python run.py --parallel -w 4

# 生成Allure报告
python run.py --report
```

### 使用behave命令执行

```bash
# 执行所有测试
behave

# 执行指定feature文件
behave features/api_example.feature

# 执行指定tag的用例
behave --tags=smoke

# 生成Allure报告
behave --format allure_behave.formatter:AllureFormatter --out allure-results
```

### 查看Allure报告

```bash
# 生成报告
allure generate allure-results -o allure-report --clean

# 打开报告
allure open allure-report
```

## 📊 测试报告

框架支持Allure测试报告，提供：

- 详细的测试执行结果
- 测试步骤截图
- 请求和响应详情
- 测试执行时间统计
- 失败用例的错误信息

## 🔧 扩展功能

### 数据库操作

```python
from behavior_framework.utils.database import Database

# 创建数据库连接
db = Database(
    db_type="mysql",
    host="localhost",
    port=3306,
    user="root",
    password="password",
    database="testdb"
)

# 执行查询
results = db.execute_query("SELECT * FROM users WHERE id = %s", (1,))

# 执行更新
db.execute_update("INSERT INTO users (name, email) VALUES (%s, %s)", ("Test", "test@example.com"))
```

### 文件读取

```python
from behavior_framework.utils.file_reader import FileReader

# 读取YAML文件
reader = FileReader()
data = reader.read_yaml("data/config.yaml")

# 读取Excel文件
data = reader.read_excel("data/test_data.xlsx", sheet_name="Sheet1")

# 读取JSON文件
data = reader.read_json("data/config.json")
```

## 🔗 Jenkins集成

### 使用Jenkinsfile

项目包含 `Jenkinsfile`，可以直接在Jenkins中使用：

1. 在Jenkins中创建Pipeline项目
2. 配置源代码管理
3. 构建触发器设置为Pipeline script from SCM
4. 运行构建

### 使用Jenkins API

```python
from jenkins_integration import JenkinsIntegration

# 连接Jenkins
jenkins = JenkinsIntegration(
    jenkins_url="http://jenkins.example.com",
    username="admin",
    api_token="your_token"
)

# 触发任务
build_number = jenkins.trigger_job("test-job", {"branch": "master"})

# 获取构建状态
status = jenkins.get_build_status("test-job", build_number)
```

## 🤝 贡献

欢迎提交 Issue 和 Pull Request 来改进框架！

## 📄 许可证

MIT License

## 📞 支持

如有问题，请提交 Issue 或联系开发团队。
