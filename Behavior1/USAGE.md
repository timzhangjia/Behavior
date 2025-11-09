# 使用说明

## 目录结构

```
Behavior/
├── behavior_framework/     # 框架核心代码
│   ├── api/               # API测试模块
│   ├── ui/                # UI测试模块
│   ├── config/            # 配置模块
│   └── utils/             # 工具模块
├── features/              # Behave测试用例目录
│   ├── steps/            # 步骤定义
│   ├── environment.py    # 环境配置
│   └── *.feature        # 测试用例文件
├── data/                 # 测试数据目录
│   └── elements/        # 元素定位配置
├── tests/               # 示例代码
├── run.py              # 测试执行入口
└── requirements.txt    # 依赖包
```

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
playwright install
```

### 2. 配置环境变量

复制 `env.example` 为 `.env` 并修改配置：

```bash
cp env.example .env
```

### 3. 编写测试用例

在 `features` 目录下创建 `.feature` 文件：

```gherkin
# language: zh-CN
功能: 登录测试
  场景: 用户登录
    当我打开浏览器
    当我打开页面"login_page"，URL为"https://example.com/login"
    当我在"username_input"元素中输入"testuser"
    当我在"password_input"元素中输入"password123"
    当我点击"login_button"元素
    那么页面URL应该包含"dashboard"
```

### 4. 配置元素定位

在 `data/elements/common.yaml` 中配置元素定位：

```yaml
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

### 5. 运行测试

```bash
# 执行所有测试
python run.py

# 执行指定feature文件
python run.py -f features/ui_example.feature

# 执行指定tag的用例
python run.py -t smoke

# 并行执行
python run.py --parallel -w 4

# 生成Allure报告
python run.py --report
```

## 常用步骤

### UI测试步骤

- `当我打开浏览器` - 打开浏览器
- `当我打开页面"{page_name}"，URL为"{url}"` - 打开页面
- `当我导航到"{url}"` - 导航到指定URL
- `当我在"{element_name}"元素中输入"{text}"` - 输入文本
- `当我点击"{element_name}"元素` - 点击元素
- `当我双击"{element_name}"元素` - 双击元素
- `当我悬停在"{element_name}"元素上` - 悬停元素
- `当我等待"{seconds}"秒` - 等待指定秒数
- `当我等待页面加载完成` - 等待页面加载
- `那么"{element_name}"元素应该可见` - 断言元素可见
- `那么"{element_name}"元素应该包含文本"{expected_text}"` - 断言元素文本
- `那么页面标题应该是"{expected_title}"` - 断言页面标题
- `那么页面URL应该包含"{expected_url}"` - 断言页面URL
- `那么我截图保存为"{filename}"` - 截图

### API测试步骤

- `当我初始化API客户端，基础URL为"{base_url}"` - 初始化API客户端
- `当我设置API请求头"{header_name}"为"{header_value}"` - 设置请求头
- `当我设置API认证为"{auth_type}"，凭证为"{credentials}"` - 设置认证
- `当我发送"{method}"请求到"{endpoint}"` - 发送请求
- `当我发送"{method}"请求到"{endpoint}"，请求体为` - 发送带请求体的请求
- `当我发送"{method}"请求到"{endpoint}"，查询参数为` - 发送带查询参数的请求
- `那么响应状态码应该是"{expected_status}"` - 断言状态码
- `那么响应状态码应该是成功的` - 断言响应成功
- `那么响应头"{header_name}"应该是"{expected_value}"` - 断言响应头
- `那么响应JSON中"{key}"的值应该是"{expected_value}"` - 断言JSON值
- `那么响应应该包含文本"{expected_text}"` - 断言响应文本
- `那么响应应该是JSON格式` - 断言JSON格式
- `那么我保存响应JSON中"{key}"的值为"{variable_name}"` - 保存变量

## Tag使用

使用tag可以组织和管理测试用例：

```gherkin
@api @smoke
场景: 获取用户信息
  ...

@ui @regression
场景: 登录测试
  ...
```

执行指定tag的用例：

```bash
python run.py -t smoke        # 执行smoke标签的用例
python run.py -t api          # 执行api标签的用例
python run.py -t smoke,api    # 执行多个标签的用例
```

## 元素定位类型

在YAML配置文件中，支持以下定位类型：

- `id` - ID定位
- `class` - 类名定位
- `css` - CSS选择器定位
- `xpath` - XPath定位
- `name` - name属性定位

示例：

```yaml
login_page:
  username_input: 
    type: "id"
    value: "username"
  submit_button:
    type: "css"
    value: "button[type='submit']"
  search_box:
    type: "xpath"
    value: "//input[@name='search']"
```

## 数据库操作

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

## 文件读取

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

## Allure报告

生成Allure报告：

```bash
# 运行测试并生成报告
python run.py --report

# 或者手动生成
allure generate allure-results -o allure-report --clean

# 打开报告
allure open allure-report
```

## Jenkins集成

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

## 常见问题

### 1. 浏览器无法启动

确保已安装Playwright浏览器：

```bash
playwright install
```

### 2. Allure报告无法生成

确保已安装Allure命令行工具：

```bash
# Windows
scoop install allure

# macOS
brew install allure

# Linux
# 下载并解压Allure，添加到PATH
```

### 3. 并行测试无法执行

确保已安装behave-parallel：

```bash
pip install behave-parallel
```

### 4. 元素定位失败

检查：
1. YAML配置文件中的元素定位信息是否正确
2. 页面名称是否匹配
3. 元素是否已加载完成

## 更多信息

详细文档请参考 README.md


