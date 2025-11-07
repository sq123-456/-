from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import os
import json
import anthropic
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your-secret-key-here-change-in-production'  # 用于session加密

# 数据存储目录
DATA_DIR = 'data'
USERS_FILE = os.path.join(DATA_DIR, 'users.txt')
CHAT_HISTORY_DIR = os.path.join(DATA_DIR, 'chat_history')

# MiniMax API配置（使用Anthropic SDK）
MINIMAX_API_KEY = 'eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJHcm91cE5hbWUiOiLlrZnmuIUiLCJVc2VyTmFtZSI6IuWtmea4hSIsIkFjY291bnQiOiIiLCJTdWJqZWN0SUQiOiIxOTg2NDQ4ODk4NTc4NzE0NjMyIiwiUGhvbmUiOiIxOTkyMTY1OTkxNyIsIkdyb3VwSUQiOiIxOTg2NDQ4ODk4NTc0NTIwMzI4IiwiUGFnZU5hbWUiOiIiLCJNYWlsIjoiIiwiQ3JlYXRlVGltZSI6IjIwMjUtMTEtMDcgMDI6MDY6MDQiLCJUb2tlblR5cGUiOjEsImlzcyI6Im1pbmltYXgifQ.um7Xk2qYnKimT11-_0USwkbypJf2D4nxHnw2qjjn8BrRgR5OxXMl2y6HCkc0O1ncMyxq40vEGDSPS3wN8DTLNZ34I9Sr0_FnV-ssqWvPuiET_bD3EyCtsgR-lp-zB6VuxS8ZP1gaNyBYDf7if_YGqiTk1eFrzK4fD0DJnOTBU0oTPKu31coDLvbpYLuC4GxuuTfBMaUJnEINe0zLW0NrK9XCiWy197ayZqyZgYhI6CSl7p6Oef5QE8NBMbemLyrtEQgsmZweYln7kQwIm1fS7Jn6tH9GfSGKsuWwhq-e6w2QTsWlXydzQuYjj0KjnKcWDhGCgSgE-GP_0VgRyuVuTw'  # 请替换为你的MiniMax API密钥
MINIMAX_BASE_URL = 'https://api.minimaxi.com/anthropic'  # MiniMax官方API地址
MINIMAX_MODEL = 'MiniMax-M2'  # MiniMax模型名称

# 确保数据目录存在
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(CHAT_HISTORY_DIR, exist_ok=True)

# 初始化用户文件
if not os.path.exists(USERS_FILE):
    with open(USERS_FILE, 'w', encoding='utf-8') as f:
        pass


# 用户管理函数
def read_users():
    """读取所有用户"""
    users = {}
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and '|' in line:
                    username, password = line.split('|', 1)
                    users[username] = password
    return users


def save_user(username, password):
    """保存新用户"""
    with open(USERS_FILE, 'a', encoding='utf-8') as f:
        f.write(f'{username}|{password}\n')


def verify_user(username, password):
    """验证用户"""
    users = read_users()
    return users.get(username) == password


# 对话历史管理函数
def get_chat_history_file(username):
    """获取用户的对话历史文件路径"""
    return os.path.join(CHAT_HISTORY_DIR, f'{username}_history.json')


def load_chat_history(username):
    """加载用户的对话历史"""
    history_file = get_chat_history_file(username)
    if os.path.exists(history_file):
        with open(history_file, 'r', encoding='utf-8') as f:
            try:
                return json.load(f)
            except:
                return []
    return []


def save_chat_history(username, history):
    """保存用户的对话历史"""
    history_file = get_chat_history_file(username)
    with open(history_file, 'w', encoding='utf-8') as f:
        json.dump(history, f, ensure_ascii=False, indent=2)


# MiniMax API调用函数（使用Anthropic SDK）
def call_minimax_api(messages):
    """调用MiniMax API（使用官方Anthropic SDK方式）"""
    try:
        # 创建Anthropic客户端，指向MiniMax API
        # MiniMax需要在Authorization header中使用Bearer token格式
        # 注意：不能同时设置api_key和Authorization头，会冲突
        # 因此api_key传入空字符串，完全通过default_headers传递认证信息
        client = anthropic.Anthropic(
            base_url=MINIMAX_BASE_URL,
            api_key="sk-placeholder",  # 占位符，实际认证通过default_headers
            default_headers={
                "Authorization": f"Bearer {MINIMAX_API_KEY}"
            }
        )
        
        # 系统提示，让模型扮演医生角色
        system_prompt = """你是一位专业、温暖、耐心的AI医疗助手，具备丰富的医学知识。

你的角色定位：
- 你是用户的健康顾问，可以直接回答医疗健康问题
- 根据用户描述的症状，提供专业的初步评估和建议
- 询问必要的补充信息以更好地了解病情
- 提供具体、实用的健康建议和注意事项

交流风格：
- 使用温暖、关切的语气，让用户感到被关心
- 用通俗易懂的语言解释医学术语
- 回答要有条理性，使用列表或分段让内容清晰
- 保持专业但不要太过正式和冷漠

重要原则：
1. 你的建议仅供参考，不能替代专业医生的面对面诊断
2. 遇到以下情况，必须建议用户立即就医：
   - 严重或突发的症状（如剧烈疼痛、呼吸困难、大出血等）
   - 涉及急症的症状（如胸痛、中风迹象、严重外伤等）
   - 症状持续加重或长期未愈
3. 提供建议时要考虑安全性，避免推荐可能有风险的自我治疗
4. 不要说"我无法调取系统资源"、"我只是AI"等破坏角色感的话
5. 直接以医疗助手的身份回答问题，自然地提供帮助

记住：你的目标是成为用户值得信赖的健康顾问，帮助他们更好地理解和管理自己的健康状况。"""
        
        # 转换消息格式为Anthropic SDK格式
        # MiniMax可能需要简化的消息格式
        formatted_messages = []
        for msg in messages:
            formatted_messages.append({
                "role": msg["role"],
                "content": msg["content"]  # 直接使用字符串，不包装成数组
            })
        
        # 调用API
        message = client.messages.create(
            model=MINIMAX_MODEL,
            max_tokens=1024,
            system=system_prompt,
            messages=formatted_messages
        )
        
        # 提取回复内容（可能包含thinking和text）
        response_text = ""
        
        for block in message.content:
            if block.type == "thinking":
                # 记录thinking内容用于调试
                if hasattr(block, 'thinking') and block.thinking:
                    print(f"[DEBUG] AI思考过程长度: {len(block.thinking)}")
            elif block.type == "text":
                # 提取text内容
                if hasattr(block, 'text') and block.text:
                    response_text += block.text
        
        return response_text if response_text else '抱歉，我现在无法回答。请稍后再试。'
            
    except anthropic.APIError as e:
        print(f'MiniMax API调用错误: {e}')
        return f'抱歉，服务暂时不可用。错误信息：{str(e)}'
    except Exception as e:
        print(f'未知错误: {e}')
        return f'抱歉，发生了未知错误：{str(e)}'


# 路由
@app.route('/')
def index():
    """首页，重定向到登录页"""
    if 'username' in session:
        return redirect(url_for('chat'))
    return redirect(url_for('login'))


@app.route('/login')
def login():
    """登录页面"""
    return render_template('login.html')


@app.route('/register')
def register():
    """注册页面"""
    return render_template('register.html')


@app.route('/chat')
def chat():
    """对话页面"""
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('chat.html', username=session['username'])


@app.route('/api/login', methods=['POST'])
def api_login():
    """登录API"""
    data = request.get_json()
    username = data.get('username', '').strip()
    password = data.get('password', '')
    
    if not username or not password:
        return jsonify({'success': False, 'message': '用户名和密码不能为空'})
    
    if verify_user(username, password):
        session['username'] = username
        return jsonify({'success': True, 'message': '登录成功'})
    else:
        return jsonify({'success': False, 'message': '用户名或密码错误'})


@app.route('/api/register', methods=['POST'])
def api_register():
    """注册API"""
    data = request.get_json()
    username = data.get('username', '').strip()
    password = data.get('password', '')
    
    if not username or not password:
        return jsonify({'success': False, 'message': '用户名和密码不能为空'})
    
    if len(username) < 3:
        return jsonify({'success': False, 'message': '用户名至少需要3个字符'})
    
    if len(password) < 6:
        return jsonify({'success': False, 'message': '密码至少需要6个字符'})
    
    users = read_users()
    if username in users:
        return jsonify({'success': False, 'message': '用户名已存在'})
    
    save_user(username, password)
    return jsonify({'success': True, 'message': '注册成功，请登录'})


@app.route('/api/logout', methods=['POST'])
def api_logout():
    """登出API"""
    session.pop('username', None)
    return jsonify({'success': True, 'message': '已退出登录'})


@app.route('/api/chat', methods=['POST'])
def api_chat():
    """对话API"""
    if 'username' not in session:
        return jsonify({'success': False, 'message': '请先登录'})
    
    data = request.get_json()
    user_message = data.get('message', '').strip()
    
    if not user_message:
        return jsonify({'success': False, 'message': '消息不能为空'})
    
    username = session['username']
    
    # 加载对话历史
    history = load_chat_history(username)
    
    # 构建消息列表（只保留最近10轮对话作为上下文）
    messages = []
    recent_history = history[-10:] if len(history) > 10 else history
    for item in recent_history:
        messages.append({'role': 'user', 'content': item['user']})
        messages.append({'role': 'assistant', 'content': item['assistant']})
    
    # 添加当前用户消息
    messages.append({'role': 'user', 'content': user_message})
    
    # 调用MiniMax API
    assistant_message = call_minimax_api(messages)
    
    # 保存到历史记录
    history.append({
        'user': user_message,
        'assistant': assistant_message,
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    })
    save_chat_history(username, history)
    
    return jsonify({
        'success': True,
        'message': assistant_message
    })


@app.route('/api/history', methods=['GET'])
def api_history():
    """获取对话历史API"""
    if 'username' not in session:
        return jsonify({'success': False, 'message': '请先登录'})
    
    username = session['username']
    history = load_chat_history(username)
    
    return jsonify({
        'success': True,
        'history': history
    })


@app.route('/api/clear_history', methods=['POST'])
def api_clear_history():
    """清空对话历史API"""
    if 'username' not in session:
        return jsonify({'success': False, 'message': '请先登录'})
    
    username = session['username']
    save_chat_history(username, [])
    
    return jsonify({
        'success': True,
        'message': '对话历史已清空'
    })


if __name__ == '__main__':
    print('AI问诊小医生启动中...')
    print('请在浏览器中访问: http://127.0.0.1:5000')
    app.run(debug=True, host='127.0.0.1', port=5000)

