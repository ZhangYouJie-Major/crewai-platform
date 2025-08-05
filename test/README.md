# CrewAI Platform 测试文档

## 📋 测试概述

本测试套件为 CrewAI Platform 提供全面的功能测试，确保系统的各个模块能够正常工作。

## 🏗️ 测试结构

### 测试基础设施

- **`test_config.py`** - 测试配置文件，包含API端点、测试账号等配置
- **`test_base.py`** - 测试基类，提供通用的测试工具和方法
- **`run_tests.py`** - 统一测试执行脚本，支持选择性运行测试

### 测试模块

| 模块 | 文件 | 描述 |
|------|------|------|
| 🔐 认证测试 | `test_auth.py` | 登录、登出、Token验证等认证相关测试 |
| 🤖 Agent管理测试 | `test_agent_management.py` | Agent的CRUD操作、克隆、启用/禁用等功能测试 |
| 🔧 MCP工具管理测试 | `test_mcp_tool_management.py` | MCP工具的CRUD操作、健康检查等功能测试 |
| 📚 字典管理测试 | `test_dictionary_management.py` | 字典的CRUD操作、树结构、父子关系等功能测试 |

## 🚀 快速开始

### 1. 环境准备

确保后端服务正在运行：

```bash
# 启动后端服务
cd backend
python manage.py runserver
```

### 2. 运行测试

#### 查看可用测试套件

```bash
cd test
python run_tests.py --list
```

#### 运行单个测试套件

```bash
# 运行认证测试
python run_tests.py --suite auth

# 运行Agent管理测试
python run_tests.py --suite agent

# 运行MCP工具管理测试
python run_tests.py --suite mcp

# 运行字典管理测试
python run_tests.py --suite dictionary
```

#### 运行多个测试套件

```bash
# 运行认证和Agent管理测试
python run_tests.py --suite auth,agent

# 运行所有测试
python run_tests.py --all
```

#### 保存测试报告

```bash
# 运行所有测试并保存报告
python run_tests.py --all --save-report

# 指定输出文件名
python run_tests.py --suite auth --save-report --output auth_report.txt
```

## 📊 测试账号

测试使用以下账号：

| 账号类型 | 用户名 | 密码 | 用途 |
|----------|--------|------|------|
| admin | admin | 1234qwer* | 管理员账号，用于所有测试 |
| testuser | testuser | testpass123 | 普通用户账号，用于权限测试 |

## 🔧 测试配置

### API配置

- **基础URL**: `http://localhost:8000/api`
- **超时时间**: 30秒
- **日志级别**: INFO

### 测试数据

测试会自动创建和清理测试数据，包括：

- Agent测试数据
- MCP工具测试数据
- 字典测试数据
- 用户测试数据

## 📋 测试用例详情

### 🔐 认证测试 (`test_auth.py`)

| 测试用例 | 描述 | 预期结果 |
|----------|------|----------|
| `test_admin_login_success` | 管理员登录成功 | 返回200状态码和访问令牌 |
| `test_admin_login_failure` | 管理员登录失败（错误密码） | 返回401状态码 |
| `test_invalid_username_login` | 无效用户名登录 | 返回401状态码 |
| `test_empty_credentials_login` | 空凭据登录 | 返回400状态码 |
| `test_token_refresh` | Token刷新 | 返回新的访问令牌 |
| `test_token_validation` | Token验证 | 有效Token可访问API，无效Token被拒绝 |
| `test_logout` | 登出功能 | 登出后无法访问受保护API |
| `test_concurrent_login` | 并发登录 | 多个用户可同时登录 |

### 🤖 Agent管理测试 (`test_agent_management.py`)

| 测试用例 | 描述 | 预期结果 |
|----------|------|----------|
| `test_get_llm_models` | 获取可用LLM模型 | 返回可用模型列表 |
| `test_create_agent` | 创建Agent | 成功创建Agent并返回ID |
| `test_get_agent_list` | 获取Agent列表 | 返回所有Agent列表 |
| `test_get_agent_detail` | 获取Agent详情 | 返回指定Agent的详细信息 |
| `test_update_agent` | 更新Agent | 成功更新Agent信息 |
| `test_clone_agent` | 克隆Agent | 成功克隆Agent并创建新实例 |
| `test_toggle_agent_status` | 切换Agent状态 | 成功启用/禁用Agent |
| `test_disable_agent` | 禁用Agent | 禁用Agent但仍保留在列表中 |
| `test_delete_agent` | 删除Agent | 成功删除Agent |

### 🔧 MCP工具管理测试 (`test_mcp_tool_management.py`)

| 测试用例 | 描述 | 预期结果 |
|----------|------|----------|
| `test_create_mcp_tool` | 创建MCP工具 | 成功创建工具并返回ID |
| `test_get_mcp_tool_list` | 获取工具列表 | 返回所有MCP工具列表 |
| `test_get_mcp_tool_detail` | 获取工具详情 | 返回指定工具的详细信息 |
| `test_update_mcp_tool` | 更新工具 | 成功更新工具信息 |
| `test_health_check` | 健康检查 | 返回工具健康状态 |
| `test_health_check_invalid_tool` | 无效工具健康检查 | 返回404状态码 |
| `test_disable_mcp_tool` | 禁用工具 | 禁用工具但仍保留在列表中 |
| `test_delete_mcp_tool` | 删除工具 | 成功删除工具 |
| `test_mcp_tool_validation` | 数据验证 | 无效数据返回400状态码 |
| `test_mcp_tool_duplicate_name` | 名称重复验证 | 重复名称返回400状态码 |

### 📚 字典管理测试 (`test_dictionary_management.py`)

| 测试用例 | 描述 | 预期结果 |
|----------|------|----------|
| `test_create_dictionary` | 创建字典 | 成功创建字典并返回ID |
| `test_get_dictionary_list` | 获取字典列表 | 返回所有字典列表 |
| `test_get_dictionary_detail` | 获取字典详情 | 返回指定字典的详细信息 |
| `test_update_dictionary` | 更新字典 | 成功更新字典信息 |
| `test_create_dictionary_with_parent` | 创建带父级的字典 | 成功创建子字典并建立父子关系 |
| `test_get_dictionary_tree` | 获取字典树结构 | 返回层级化的字典树 |
| `test_dictionary_hierarchy` | 字典层级关系 | 验证多级字典的父子关系 |
| `test_move_dictionary` | 移动字典位置 | 成功改变字典的父级关系 |
| `test_delete_dictionary_with_children` | 删除带子级的字典 | 有子级时拒绝删除，无子级时成功删除 |
| `test_dictionary_validation` | 数据验证 | 无效数据返回400状态码 |
| `test_dictionary_duplicate_name` | 名称重复验证 | 重复名称返回400状态码 |

## 🛠️ 故障排除

### 常见问题

1. **连接错误**
   - 确保后端服务正在运行
   - 检查API基础URL配置是否正确

2. **认证失败**
   - 确保测试账号存在且密码正确
   - 检查数据库连接

3. **测试数据清理失败**
   - 检查数据库权限
   - 手动清理测试数据

### 日志文件

测试运行时会生成详细的日志文件，格式为：
```
test_{测试套件名}_{时间戳}.log
```

### 调试模式

如需更详细的调试信息，可以修改 `test_config.py` 中的日志级别：

```python
LOG_LEVEL = "DEBUG"  # 改为DEBUG级别
```

## 📈 持续集成

### 自动化测试

可以将测试集成到CI/CD流程中：

```bash
# 在CI环境中运行所有测试
python run_tests.py --all --save-report

# 检查退出码
if [ $? -eq 0 ]; then
    echo "所有测试通过"
else
    echo "部分测试失败"
    exit 1
fi
```

### 测试覆盖率

建议定期运行测试并检查覆盖率，确保代码质量。

## 🤝 贡献指南

### 添加新测试

1. 创建新的测试文件，继承 `BaseTester`
2. 实现测试方法，使用断言验证结果
3. 在 `run_tests.py` 中注册新的测试套件
4. 更新本文档

### 测试规范

- 每个测试方法应该有明确的描述
- 使用有意义的测试数据
- 确保测试的独立性和可重复性
- 及时清理测试数据

## 📞 支持

如有问题或建议，请：

1. 查看日志文件获取详细错误信息
2. 检查测试配置是否正确
3. 确保后端服务正常运行
4. 联系开发团队获取支持 