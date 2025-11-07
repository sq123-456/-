# MiniMax API 配置示例（使用Anthropic SDK方式）
# 请复制此文件内容到 app.py 中的相应位置

# 方式1：直接在app.py中配置
MINIMAX_API_KEY = 'your_api_key'  # 替换为你的MiniMax API密钥
MINIMAX_BASE_URL = 'https://api.minimaxi.com/anthropic'  # MiniMax官方API地址
MINIMAX_MODEL = 'MiniMax-M2'  # MiniMax模型名称

# 方式2：使用环境变量（推荐用于生产环境）
# import os
# MINIMAX_API_KEY = os.getenv('MINIMAX_API_KEY', 'your_default_key')
# MINIMAX_BASE_URL = os.getenv('MINIMAX_BASE_URL', 'https://api.minimaxi.com/anthropic')
# MINIMAX_MODEL = os.getenv('MINIMAX_MODEL', 'MiniMax-M2')

"""
如何获取MiniMax API密钥：

1. 访问 MiniMax 开放平台：https://www.minimaxi.com/
2. 注册并登录账号
3. 在控制台中创建应用
4. 获取 API Key (API密钥)
5. 将获取的API密钥填入上面的 MINIMAX_API_KEY 配置项

调用方式说明：
- 本项目使用官方推荐的 Anthropic SDK 方式调用 MiniMax API
- base_url: https://api.minimaxi.com/anthropic
- model: MiniMax-M2
- 支持思维链（thinking）功能，可以看到AI的思考过程

注意事项：
- 请妥善保管你的API密钥，不要上传到公共代码仓库
- MiniMax提供免费试用额度，具体请查看官网说明
- 如果API调用失败，请检查密钥是否正确，账户额度是否充足
- 确保已安装 anthropic 库: pip install anthropic
"""

