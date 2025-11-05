# 微信公众号文章搜索 MCP

一款基于 Model Context Protocol (MCP) 的微信公众号文章搜索工具,帮助 AI 助手快速搜索和获取微信公众号文章内容。

## ✨ 特性

- 🔍 **智能搜索**: 支持关键词或自然语言搜索微信公众号文章
- 📄 **完整内容**: 自动抓取文章完整正文,供 LLM 分析
- ⚡ **高效并发**: 异步并发抓取多篇文章,速度快
- 🔗 **真实链接**: 自动解析搜狗跳转链接,获取文章真实 URL
- 🤖 **AI 友好**: 返回结构化 Markdown,由调用的 LLM 进行智能总结
- 🎯 **职责清晰**: MCP 专注数据获取,LLM 专注内容理解

## 📋 系统要求

- Python 3.8+
- macOS / Windows / Linux
- 支持 MCP 的 AI 客户端 (Claude Desktop、Continue 等)

## 🚀 快速开始

### 1. 安装依赖

```bash
# 克隆项目
cd wechat-mcp-summarizer

# 创建虚拟环境
python3 -m venv .venv

# 激活虚拟环境
source .venv/bin/activate  # macOS/Linux
# .venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置 MCP 客户端

#### Claude Desktop

编辑配置文件:
- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`

添加以下配置:

```json
{
  "mcpServers": {
    "wechat-search": {
      "command": "python",
      "args": ["/path/to/wechat-mcp-summarizer/mcp_server.py"]
    }
  }
}
```

#### Continue (VS Code)

编辑 `~/.continue/config.json`:

```json
{
  "experimental": {
    "modelContextProtocolServers": [
      {
        "transport": {
          "type": "stdio",
          "command": "python",
          "args": ["/path/to/wechat-mcp-summarizer/mcp_server.py"]
        }
      }
    ]
  }
}
```

#### Claude Code (CLI)

在项目目录下创建或编辑 `CLAUDE.md` 文件:

```markdown
# MCP Servers

## wechat-search
command: python
args: ["/path/to/wechat-mcp-summarizer/mcp_server.py"]
```

或者在全局配置 `~/.config/claude/settings.json` 中添加:

```json
{
  "mcpServers": {
    "wechat-search": {
      "command": "python",
      "args": ["/absolute/path/to/wechat-mcp-summarizer/mcp_server.py"]
    }
  }
}
```

**注意**: 
- 必须使用绝对路径
- 确保 Python 环境中已安装所有依赖
- 如果使用虚拟环境,可以指定虚拟环境的 Python:
  ```json
  {
    "mcpServers": {
      "wechat-search": {
        "command": "/absolute/path/to/.venv/bin/python",
        "args": ["/absolute/path/to/mcp_server.py"]
      }
    }
  }
  ```

### 3. 重启客户端

- **Claude Desktop**: 完全退出后重新打开
- **VS Code**: 重新加载窗口或重启 VS Code
- **Claude Code**: 无需重启,配置文件会自动加载

## 💡 使用示例

### 在 Claude Code 中使用

启动 Claude Code 后,可以直接使用自然语言调用工具:

```bash
# 在终端启动 Claude Code
claude

# 在 Claude Code 中输入
> 帮我搜索关于人工智能在医疗领域应用的微信文章并总结
```

Claude Code 会自动:
1. 识别需要调用 `search_wechat_articles` 工具
2. 使用合适的参数执行搜索
3. 获取文章内容后进行分析和总结
4. 返回结构化的总结结果

### 在 Claude Desktop 中使用

```
用户: 帮我搜索关于人工智能在医疗领域应用的微信文章并总结
```

**工作流程**:
1. Claude 调用 MCP 工具: `search_wechat_articles("人工智能 医疗", count=3)`
2. MCP 返回 3 篇文章的完整内容
3. Claude 自动分析并生成综合总结
4. 用户可以追问细节或查看原文链接

### 指定文章数量

```
用户: 搜索关于"区块链技术"的微信文章,获取 5 篇,并从监管角度分析
```

MCP 会获取 5 篇文章,Claude 根据"监管角度"进行针对性分析。

### 多轮对话

```
用户: 搜索大模型应用的文章
Claude: [返回搜索结果和总结]

用户: 这些文章中提到了哪些具体的应用案例?
Claude: [基于已获取的内容深入分析,无需重新搜索]

用户: 第二篇文章的作者观点是什么?
Claude: [直接从已有内容中提取信息]
```

## 🛠️ 工具说明

### `search_wechat_articles`

搜索微信公众号文章并返回完整内容。

**参数**:
- `query` (必填): 搜索关键词或自然语言描述
- `count` (可选): 获取文章数量,默认 3,范围 1-10

**返回格式**:
```markdown
# 微信文章搜索结果

**搜索关键词**: 人工智能 医疗
**找到文章数**: 3

---

## 文章 1: AI 赋能医疗:从影像诊断到精准治疗

**公众号**: 健康科技前沿
**链接**: https://mp.weixin.qq.com/s/xxxxx

### 正文内容

[完整文章正文...]

---

## 文章 2: ...
```

## ⚙️ 配置说明

编辑 `config.py` 自定义配置:

```python
# 默认获取文章数量
DEFAULT_ARTICLE_COUNT = 3

# 最大获取文章数量
MAX_ARTICLE_COUNT = 10

# 每篇文章的最大字符数(避免超出 LLM 上下文窗口)
MAX_ARTICLE_LENGTH = 10000

# 并发抓取的最大数量
MAX_CONCURRENT_FETCHES = 3

# 请求超时时间(秒)
REQUEST_TIMEOUT = 30
```

## 📁 项目结构

```
wechat-mcp-summarizer/
├── mcp_server.py              # MCP 服务端主程序
├── modules/
│   ├── __init__.py
│   ├── weixin_search.py       # 微信搜索模块
│   └── article_processor.py   # 文章抓取和解析模块
├── config.py                  # 配置文件
├── requirements.txt           # 依赖列表
└── README.md                  # 本文档
```

## 🔧 故障排查

### MCP 工具未显示

1. 检查配置文件路径是否正确
2. 确认 Python 路径和脚本路径使用绝对路径
3. 重启 MCP 客户端
4. 查看客户端日志文件

### 搜索无结果

- 尝试更换关键词
- 检查网络连接
- 可能被搜狗反爬虫拦截,稍后重试

### 文章内容抓取失败

⚠️ **重要说明**: 由于搜狗和微信的反爬虫机制,直接抓取文章完整内容可能会失败。在这种情况下:
- MCP 仍会返回文章标题、公众号名称、摘要和链接
- 用户可以通过链接手动访问原文
- 建议使用时关注搜索和链接获取功能,而不完全依赖自动内容抓取

### 文章内容不完整

- 调整 `MAX_ARTICLE_LENGTH` 配置
- 某些文章可能包含特殊格式,解析器会尽力提取

### 请求超时

- 增加 `REQUEST_TIMEOUT` 值
- 减少 `count` 参数,分批搜索
- 检查网络状况

## 🎯 使用场景

### 内容研究
快速调研特定主题在微信生态的讨论情况,获取多维度观点。

### 舆情监控
追踪行业关键词,了解最新动态和公众反应。

### 对比分析
获取多篇文章后,让 LLM 进行观点对比、事实核查、深度分析。

### 知识整理
收集某领域的优质文章,由 LLM 整理成结构化笔记。

## ⚠️ 注意事项

### 使用限制
- 本工具仅供个人学习和研究使用
- 请勿用于商业目的或大规模爬取
- 遵守搜狗和微信的服务条款

### 版权声明
- 所有文章内容版权归原作者所有
- 本工具仅提供搜索和展示功能
- 请通过原文链接访问完整内容

### 技术风险
- 搜狗可能更新页面结构,导致解析失败
- 频繁请求可能导致 IP 被封
- 建议合理控制搜索频率

## 🗺️ 发展路线

### v1.0 (当前)
- ✅ 基础搜索功能
- ✅ 文章内容抓取
- ✅ 真实链接解析
- ✅ 并发处理优化

### v1.1 (计划中)
- 🔲 结果缓存机制
- 🔲 请求失败自动重试
- 🔲 代理 IP 支持

### v2.0 (未来)
- 🔲 时间范围过滤
- 🔲 文章质量评分
- 🔲 知乎、微博等多源搜索

## 🤝 贡献

欢迎提交 Issue 和 Pull Request!

## 📄 许可证

MIT License

## 🙏 致谢

本项目参考了以下开源项目:
- [fancyboi999/weixin_search_mcp](https://github.com/fancyboi999/weixin_search_mcp) - 微信搜索解析实现
- [Model Context Protocol](https://modelcontextprotocol.io/) - MCP 协议官方文档

## 📞 支持

如有问题或建议,请提交 [Issue](https://github.com/yourusername/wechat-mcp-summarizer/issues)。

---

**温馨提示**: 本工具将文章内容交由调用的 LLM 进行分析,因此总结质量取决于您使用的 AI 模型。推荐使用 Claude 3.5 Sonnet 或更高版本以获得最佳体验。
