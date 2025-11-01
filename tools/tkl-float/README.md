# Taokouling Float Tool

一个Windows桌面悬浮淘口令解析工具，使用Python + PySide6开发，支持全局热键、剪贴板自动检测、系统托盘等功能。

## 功能特性

- ✨ **悬浮窗口**: 始终置顶的紧凑窗口，可拖拽移动
- 📋 **剪贴板监控**: 自动检测剪贴板中的淘口令（￥xxx￥/€xxx€/9/xxx/格式）
- ⌨️ **全局热键**: Ctrl+Alt+T 快速唤起窗口并解析
- 🎯 **系统托盘**: 最小化到系统托盘，支持显示/隐藏/退出操作
- 🔄 **非阻塞解析**: 网络请求在后台线程执行，界面保持响应
- ⚙️ **配置管理**: 通过环境变量配置API参数
- 📝 **日志记录**: 带日志轮转，敏感信息自动脱敏

## 安装和使用

### 方法1：使用预编译EXE（推荐）

1. 下载 `TaokoulingFloatTool.exe`
2. 创建配置目录：`%APPDATA%\tkl-float\`
3. 复制 `.env.example` 到 `%APPDATA%\tkl-float\.env`
4. 编辑 `.env` 文件，填入您的API配置：
   ```ini
   LT_BASE_URL=https://api.lottefuture.com
   LT_APP_KEY=your_app_key_here
   LT_APP_SECRET=your_app_secret_here
   LT_INVITE_CODE=your_invite_code_here
   LT_TIMEOUT=30
   ```
5. 双击运行 `TaokoulingFloatTool.exe`

### 方法2：从源码运行

1. 安装Python 3.8+
2. 克隆仓库并进入工具目录
3. 创建虚拟环境：
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   ```
4. 安装依赖：
   ```bash
   pip install -r requirements.txt
   ```
5. 配置环境变量（复制 `.env.example` 为 `.env` 并编辑）
6. 运行程序：
   ```bash
   python app/main.py
   ```

## 构建EXE

使用提供的构建脚本：

```bash
build.bat
```

这将创建一个单文件EXE在 `dist\TaokoulingFloatTool.exe`。

## 使用说明

### 基本操作

1. **输入淘口令**: 在输入框中输入淘口令，点击"解析"按钮
2. **自动检测**: 启用"自动检测剪贴板"后，复制淘口令会自动填充并解析
3. **查看结果**: 解析结果显示在下方结果面板中

### 高级功能

- **全局热键**: 按 `Ctrl+Alt+T` 快速唤起窗口并解析当前内容
- **系统托盘**: 点击关闭按钮会最小化到系统托盘，右键托盘图标显示菜单
- **窗口置顶**: 窗口始终保持在其他窗口之上

### 支持的淘口令格式

- ￥淘口令￥ (人民币符号)
- €淘口令€ (欧元符号)
- ₤淘口令₤ (英镑符号)
- ɂ淘口令ɂ (特殊符号)
- 9/淘口令/ (斜杠格式)

## 配置说明

程序通过环境变量进行配置，按以下优先级加载：

1. `%APPDATA%\tkl-float\.env` (Windows生产环境)
2. 项目根目录的 `.env` (开发环境)

### 配置项

| 配置项 | 必需 | 说明 |
|--------|------|------|
| `LT_BASE_URL` | 是 | API基础URL |
| `LT_APP_KEY` | 是 | 应用密钥 |
| `LT_APP_SECRET` | 是 | 应用秘钥 |
| `LT_INVITE_CODE` | 是 | 邀请码 |
| `LT_TIMEOUT` | 否 | 请求超时时间（秒），默认30 |

## 错误处理

程序提供友好的错误提示：

- **输入格式错误**: 淘口令格式无效
- **认证已过期**: 请检查API配置
- **没有权限**: API访问权限不足
- **请求频繁**: 请稍后再试
- **网络错误**: 检查网络连接
- **服务错误**: API提供商问题

## 安全特性

- 🔒 **HTTPS通信**: 默认使用HTTPS加密传输
- 🛡️ **主机白名单**: 限制出站请求目标
- 🔄 **重试机制**: 指数退避重试策略
- 📝 **日志脱敏**: 自动隐藏日志中的敏感信息
- ⏱️ **超时控制**: 分离连接和读取超时

## 项目结构

```
tools/tkl-float/
├── app/
│   ├── main.py              # 程序入口
│   ├── ui.py                # UI界面和交互逻辑
│   ├── worker.py            # 后台工作线程
│   ├── parser.py            # 解析器基础类
│   ├── settings.py          # 配置管理
│   ├── providers/
│   │   └── lottefuture.py   # LotteFuture API客户端
│   └── resources/
│       └── icon.ico         # 应用图标
├── tests/
│   ├── test_parser.py       # 解析器测试
│   ├── test_provider.py     # 提供商测试
│   └── test_ui.py           # UI测试
├── requirements.txt         # Python依赖
├── build.bat               # PyInstaller构建脚本
├── .env.example           # 配置模板
└── README.md              # 说明文档
```

## 开发和测试

### 运行测试

```bash
# 安装测试依赖
pip install pytest

# 运行所有测试
python -m pytest tests/ -v

# 运行特定测试
python -m pytest tests/test_parser.py -v
```

### 开发环境设置

1. 安装开发依赖：
   ```bash
   pip install -r requirements.txt
   pip install pytest pytest-qt
   ```

2. 运行开发版本：
   ```bash
   python app/main.py
   ```

## 故障排除

### 常见问题

**Q: 全局热键不工作？**
A: 可能是权限不足或热键被占用。程序会显示帮助提示，您仍可以手动使用。

**Q: 剪贴板检测不工作？**
A: 检查是否启用了"自动检测剪贴板"选项，某些安全软件可能阻止剪贴板访问。

**Q: 程序无法启动？**
A: 检查Python版本（需要3.8+）和依赖是否正确安装。

**Q: API请求失败？**
A: 检查网络连接和API配置，查看日志文件获取详细错误信息。

### 日志文件

日志位置：`%APPDATA%\tkl-float\logs\app.log`

日志包含：
- 程序运行状态
- API请求详情
- 错误信息（敏感信息已脱敏）

## 许可证

本项目采用MIT许可证，详见LICENSE文件。

## 贡献

欢迎提交Issue和Pull Request！

### 开发规范

- 遵循PEP 8代码风格
- 添加适当的测试用例
- 更新相关文档
- 保持向后兼容性