#!/bin/bash

# CrewAI Platform - CrewAI基础数据初始化脚本
# 创建LLM模型配置和MCP工具的基础数据

set -e

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查是否在正确的目录
if [ ! -f "manage.py" ]; then
    log_error "请在Django项目根目录运行此脚本"
    exit 1
fi

log_info "开始初始化CrewAI基础数据..."

# 设置Django设置模块
export DJANGO_SETTINGS_MODULE=crewaiplatform.settings

# 初始化基础LLM模型配置
log_info "创建基础LLM模型配置..."

python -c "
import django
django.setup()
from crewaiplatform.models import LLMModel, MCPTool

# 创建基础 LLM 模型配置
llm_models = [
    {
        'name': 'OpenAI GPT-4',
        'provider': 'openai',
        'model_name': 'gpt-4',
        'description': 'OpenAI GPT-4 模型，适用于复杂的推理和生成任务',
        'temperature': 0.7,
        'max_tokens': 4096,
        'timeout': 30,
        'api_key': 'sk-placeholder-key-replace-with-real-key',
        'is_active': False,
    },
    {
        'name': 'OpenAI GPT-3.5 Turbo',
        'provider': 'openai', 
        'model_name': 'gpt-3.5-turbo',
        'description': 'OpenAI GPT-3.5 Turbo 模型，高性价比的对话模型',
        'temperature': 0.7,
        'max_tokens': 4096,
        'timeout': 30,
        'api_key': 'sk-placeholder-key-replace-with-real-key',
        'is_active': False,
    },
    {
        'name': 'Anthropic Claude-3.5 Sonnet',
        'provider': 'anthropic',
        'model_name': 'claude-3-5-sonnet-20241022',
        'description': 'Anthropic Claude-3.5 Sonnet 模型，擅长分析和推理',
        'langchain_class': 'ChatAnthropic',
        'temperature': 0.7,
        'max_tokens': 4096,
        'timeout': 30,
        'api_key': 'sk-ant-placeholder-key-replace-with-real-key',
        'is_active': False,
    },
    {
        'name': 'Azure OpenAI GPT-4',
        'provider': 'azure_openai',
        'model_name': 'gpt-4',
        'description': 'Azure OpenAI GPT-4 模型',
        'langchain_class': 'AzureChatOpenAI',
        'api_version': '2024-02-01',
        'temperature': 0.7,
        'max_tokens': 4096,
        'timeout': 30,
        'api_key': 'placeholder-azure-key-replace-with-real-key',
        'is_active': False,
    },
    {
        'name': 'Ollama Llama3.1',
        'provider': 'ollama',
        'model_name': 'llama3.1',
        'description': 'Ollama 本地运行的 Llama3.1 模型',
        'langchain_class': 'ChatOllama',
        'api_base_url': 'http://localhost:11434',
        'temperature': 0.7,
        'timeout': 60,
        'api_key': 'ollama-no-key-required',
        'is_active': False,
    }
]

created_models = []
for model_data in llm_models:
    model, created = LLMModel.objects.get_or_create(
        name=model_data['name'],
        defaults=model_data
    )
    if created:
        created_models.append(model.name)
        print(f'✅ 创建 LLM 模型: {model.name}')
    else:
        print(f'⚡ LLM 模型已存在: {model.name}')

print(f'📊 LLM 模型初始化完成，共创建 {len(created_models)} 个新模型')
"

# 初始化基础MCP工具配置
log_info "创建基础MCP工具配置..."

python -c "
import django
django.setup()
from crewaiplatform.models import MCPTool

# 创建基础 MCP 工具配置
mcp_tools = [
    {
        'name': 'filesystem',
        'display_name': '文件系统工具',
        'description': '提供文件和目录操作功能，包括读取、写入、列举文件等',
        'version': '1.0.0',
        'server_type': 'stdio',
        'connection_config': {
            'command': 'npx',
            'args': ['-y', '@modelcontextprotocol/server-filesystem', '/tmp'],
            'env': {'DEBUG': 'false'}
        },
        'tool_schema': {
            'tools': [
                {
                    'name': 'read_file',
                    'description': '读取文件内容',
                    'inputSchema': {
                        'type': 'object',
                        'properties': {
                            'path': {'type': 'string', 'description': '文件路径'}
                        },
                        'required': ['path']
                    }
                },
                {
                    'name': 'write_file',
                    'description': '写入文件内容',
                    'inputSchema': {
                        'type': 'object',
                        'properties': {
                            'path': {'type': 'string', 'description': '文件路径'},
                            'content': {'type': 'string', 'description': '文件内容'}
                        },
                        'required': ['path', 'content']
                    }
                },
                {
                    'name': 'list_directory',
                    'description': '列举目录内容',
                    'inputSchema': {
                        'type': 'object',
                        'properties': {
                            'path': {'type': 'string', 'description': '目录路径'}
                        },
                        'required': ['path']
                    }
                }
            ]
        },
        'is_active': False,
        'is_public': True,
    },
    {
        'name': 'brave_search',
        'display_name': 'Brave 搜索工具',
        'description': '使用 Brave Search API 进行网络搜索',
        'version': '1.0.0',
        'server_type': 'stdio',
        'connection_config': {
            'command': 'npx',
            'args': ['-y', '@modelcontextprotocol/server-brave-search'],
            'env': {'BRAVE_API_KEY': 'your-brave-api-key'}
        },
        'tool_schema': {
            'tools': [
                {
                    'name': 'brave_web_search',
                    'description': '使用Brave搜索引擎搜索网络内容',
                    'inputSchema': {
                        'type': 'object',
                        'properties': {
                            'query': {'type': 'string', 'description': '搜索查询'},
                            'count': {'type': 'integer', 'description': '返回结果数量', 'default': 10}
                        },
                        'required': ['query']
                    }
                }
            ]
        },
        'is_active': False,
        'is_public': True,
    },
    {
        'name': 'github',
        'display_name': 'GitHub 工具',
        'description': '与GitHub仓库交互，包括搜索、读取文件、创建issues等',
        'version': '1.0.0',
        'server_type': 'stdio',
        'connection_config': {
            'command': 'npx',
            'args': ['-y', '@modelcontextprotocol/server-github'],
            'env': {'GITHUB_PERSONAL_ACCESS_TOKEN': 'your-github-token'}
        },
        'tool_schema': {
            'tools': [
                {
                    'name': 'search_repositories',
                    'description': '搜索GitHub仓库',
                    'inputSchema': {
                        'type': 'object',
                        'properties': {
                            'query': {'type': 'string', 'description': '搜索查询'},
                            'sort': {'type': 'string', 'description': '排序方式'}
                        },
                        'required': ['query']
                    }
                },
                {
                    'name': 'get_file_contents',
                    'description': '获取仓库文件内容',
                    'inputSchema': {
                        'type': 'object',
                        'properties': {
                            'owner': {'type': 'string', 'description': '仓库所有者'},
                            'repo': {'type': 'string', 'description': '仓库名称'},
                            'path': {'type': 'string', 'description': '文件路径'}
                        },
                        'required': ['owner', 'repo', 'path']
                    }
                }
            ]
        },
        'is_active': False,
        'is_public': True,
    },
    {
        'name': 'sqlite',
        'display_name': 'SQLite 数据库工具',
        'description': '操作SQLite数据库，执行查询和更新操作',
        'version': '1.0.0',
        'server_type': 'stdio',
        'connection_config': {
            'command': 'npx',
            'args': ['-y', '@modelcontextprotocol/server-sqlite', '/tmp/example.db'],
            'env': {}
        },
        'tool_schema': {
            'tools': [
                {
                    'name': 'query',
                    'description': '执行SQL查询',
                    'inputSchema': {
                        'type': 'object',
                        'properties': {
                            'sql': {'type': 'string', 'description': 'SQL查询语句'}
                        },
                        'required': ['sql']
                    }
                },
                {
                    'name': 'execute',
                    'description': '执行SQL命令（INSERT、UPDATE、DELETE等）',
                    'inputSchema': {
                        'type': 'object',
                        'properties': {
                            'sql': {'type': 'string', 'description': 'SQL命令'}
                        },
                        'required': ['sql']
                    }
                }
            ]
        },
        'is_active': False,
        'is_public': True,
    }
]

created_tools = []
for tool_data in mcp_tools:
    tool, created = MCPTool.objects.get_or_create(
        name=tool_data['name'],
        defaults=tool_data
    )
    if created:
        created_tools.append(tool.name)
        print(f'✅ 创建 MCP 工具: {tool.name}')
    else:
        print(f'⚡ MCP 工具已存在: {tool.name}')

print(f'🔧 MCP 工具初始化完成，共创建 {len(created_tools)} 个新工具')
"

log_success "CrewAI 基础数据初始化完成！"

log_info "初始化结果总结："
echo "  📊 已创建基础LLM模型配置（OpenAI、Anthropic、Azure、Ollama）"
echo "  🔧 已创建基础MCP工具配置（文件系统、搜索、GitHub、数据库）"
echo ""
log_warning "注意事项："
echo "  ⚠️  LLM模型和MCP工具默认为未激活状态"
echo "  🔑 请在使用前配置正确的API密钥"
echo "  🛠️  可通过Django Admin或API接口进行配置管理"
echo ""
log_info "下一步操作："
echo "  1. 访问 http://localhost:8000/admin/ 配置LLM模型"
echo "  2. 配置MCP工具的连接参数和API密钥"
echo "  3. 创建CrewAI Agent并绑定工具"
echo ""
log_success "🎉 系统已准备就绪，可以开始使用CrewAI功能！"