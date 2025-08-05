#!/bin/bash

# 字典数据初始化脚本
# 初始化LLM供应商和模型的两级字典数据

echo "开始初始化字典基础数据..."

# 进入后端目录
cd "$(dirname "$0")/../backend"

# 创建Django管理命令来初始化字典数据
python manage.py shell << 'EOF'
from crewaiplatform.models import Dictionary

print("开始初始化字典数据...")

# 1. 创建LLM供应商字典项（顶级）
providers_data = [
    {
        'code': 'openai',
        'name': 'OpenAI',
        'description': 'OpenAI公司提供的大语言模型服务',
        'sort_order': 1
    },
    {
        'code': 'google',
        'name': 'Google',
        'description': 'Google公司提供的Gemini系列模型',
        'sort_order': 2
    },
    {
        'code': 'anthropic',
        'name': 'Anthropic',
        'description': 'Anthropic公司提供的Claude系列模型',
        'sort_order': 3
    },
    {
        'code': 'baidu',
        'name': '百度',
        'description': '百度公司提供的文心一言系列模型',
        'sort_order': 4
    },
    {
        'code': 'alibaba',
        'name': '阿里云',
        'description': '阿里云提供的通义千问系列模型',
        'sort_order': 5
    },
    {
        'code': 'tencent',
        'name': '腾讯',
        'description': '腾讯公司提供的混元系列模型',
        'sort_order': 6
    },
    {
        'code': 'zhipu',
        'name': '智谱AI',
        'description': '智谱AI提供的GLM系列模型',
        'sort_order': 7
    },
    {
        'code': 'moonshot',
        'name': 'Moonshot',
        'description': 'Moonshot AI提供的Kimi系列模型',
        'sort_order': 8
    }
]

# 创建供应商字典项
provider_items = {}
for provider_data in providers_data:
    provider_item, created = Dictionary.objects.get_or_create(
        code=provider_data['code'],
        defaults={
            'name': provider_data['name'],
            'description': provider_data['description'],
            'is_active': True,
            'sort_order': provider_data['sort_order']
        }
    )
    provider_items[provider_data['code']] = provider_item
    if created:
        print(f"创建供应商: {provider_item.name}")
    else:
        print(f"供应商已存在: {provider_item.name}")

# 2. 创建模型数据（二级字典项）
models_data = {
    'openai': [
        {'code': 'gpt-4', 'name': 'GPT-4', 'description': 'OpenAI最先进的大语言模型', 'sort_order': 1},
        {'code': 'gpt-4-turbo', 'name': 'GPT-4 Turbo', 'description': 'GPT-4的优化版本，速度更快', 'sort_order': 2},
        {'code': 'gpt-3.5-turbo', 'name': 'GPT-3.5 Turbo', 'description': '经典的GPT-3.5模型', 'sort_order': 3},
        {'code': 'gpt-4o', 'name': 'GPT-4o', 'description': 'GPT-4的多模态版本', 'sort_order': 4},
        {'code': 'gpt-4o-mini', 'name': 'GPT-4o Mini', 'description': 'GPT-4o的轻量版本', 'sort_order': 5}
    ],
    'google': [
        {'code': 'gemini-pro', 'name': 'Gemini Pro', 'description': 'Google的专业级大语言模型', 'sort_order': 1},
        {'code': 'gemini-1.5-pro', 'name': 'Gemini 1.5 Pro', 'description': 'Gemini Pro的升级版本', 'sort_order': 2},
        {'code': 'gemini-ultra', 'name': 'Gemini Ultra', 'description': 'Google最强的大语言模型', 'sort_order': 3},
        {'code': 'gemini-nano', 'name': 'Gemini Nano', 'description': 'Gemini的轻量版本', 'sort_order': 4}
    ],
    'anthropic': [
        {'code': 'claude-3-opus', 'name': 'Claude 3 Opus', 'description': 'Claude 3系列的最强版本', 'sort_order': 1},
        {'code': 'claude-3-sonnet', 'name': 'Claude 3 Sonnet', 'description': 'Claude 3系列的平衡版本', 'sort_order': 2},
        {'code': 'claude-3-haiku', 'name': 'Claude 3 Haiku', 'description': 'Claude 3系列的快速版本', 'sort_order': 3},
        {'code': 'claude-2', 'name': 'Claude 2', 'description': 'Claude的第二代模型', 'sort_order': 4}
    ],
    'baidu': [
        {'code': 'ernie-bot', 'name': '文心一言', 'description': '百度文心一言大语言模型', 'sort_order': 1},
        {'code': 'ernie-bot-turbo', 'name': '文心一言 Turbo', 'description': '文心一言的快速版本', 'sort_order': 2},
        {'code': 'ernie-bot-4', 'name': '文心一言 4.0', 'description': '文心一言的最新版本', 'sort_order': 3},
        {'code': 'ernie-3.5', 'name': 'ERNIE 3.5', 'description': 'ERNIE 3.5模型', 'sort_order': 4}
    ],
    'alibaba': [
        {'code': 'qwen-max', 'name': '通义千问 Max', 'description': '通义千问的最强版本', 'sort_order': 1},
        {'code': 'qwen-plus', 'name': '通义千问 Plus', 'description': '通义千问的增强版本', 'sort_order': 2},
        {'code': 'qwen-turbo', 'name': '通义千问 Turbo', 'description': '通义千问的快速版本', 'sort_order': 3},
        {'code': 'qwen-7b', 'name': 'Qwen-7B', 'description': '70亿参数的通义千问模型', 'sort_order': 4}
    ],
    'tencent': [
        {'code': 'hunyuan-pro', 'name': '混元 Pro', 'description': '腾讯混元的专业版本', 'sort_order': 1},
        {'code': 'hunyuan-standard', 'name': '混元标准版', 'description': '腾讯混元的标准版本', 'sort_order': 2},
        {'code': 'hunyuan-lite', 'name': '混元轻量版', 'description': '腾讯混元的轻量版本', 'sort_order': 3}
    ],
    'zhipu': [
        {'code': 'glm-4', 'name': 'GLM-4', 'description': '智谱AI的第四代GLM模型', 'sort_order': 1},
        {'code': 'glm-3-turbo', 'name': 'GLM-3 Turbo', 'description': 'GLM-3的快速版本', 'sort_order': 2},
        {'code': 'chatglm-6b', 'name': 'ChatGLM-6B', 'description': '60亿参数的ChatGLM模型', 'sort_order': 3}
    ],
    'moonshot': [
        {'code': 'moonshot-v1-8k', 'name': 'Moonshot v1 8K', 'description': 'Moonshot v1 8K上下文版本', 'sort_order': 1},
        {'code': 'moonshot-v1-32k', 'name': 'Moonshot v1 32K', 'description': 'Moonshot v1 32K上下文版本', 'sort_order': 2},
        {'code': 'moonshot-v1-128k', 'name': 'Moonshot v1 128K', 'description': 'Moonshot v1 128K上下文版本', 'sort_order': 3}
    ]
}

# 创建模型字典项
for provider_code, models in models_data.items():
    if provider_code in provider_items:
        parent_item = provider_items[provider_code]
        for model_data in models:
            model_item, created = Dictionary.objects.get_or_create(
                parent=parent_item,
                code=model_data['code'],
                defaults={
                    'name': model_data['name'],
                    'description': model_data['description'],
                    'is_active': True,
                    'sort_order': model_data['sort_order']
                }
            )
            if created:
                print(f"创建模型: {parent_item.name} -> {model_item.name}")
            else:
                print(f"模型已存在: {parent_item.name} -> {model_item.name}")

print("字典数据初始化完成！")

# 统计信息
total_providers = Dictionary.objects.filter(parent__isnull=True).count()
total_models = Dictionary.objects.filter(parent__isnull=False).count()
print(f"总计: {total_providers} 个供应商, {total_models} 个模型")

EOF

echo "字典基础数据初始化完成！"