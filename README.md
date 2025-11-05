# 微信公众号文章搜索 MCP

一款基于 Model Context Protocol (MCP) 的微信公众号文章搜索工具,帮助 AI 助手快速搜索和获取微信公众号文章内容。

> 🚀 **新用户?** 查看 [Claude Code使用指南.md](./Claude-Code使用指南.md) 快速上手!

## 📚 文档导航

- **新手入门**: [Claude-Code使用指南.md](./Claude-Code使用指南.md) - 5分钟快速开始
- **快速开始**: [快速开始.md](./快速开始.md) - 配置和基础使用
- **测试报告**: [测试报告.md](./测试报告.md) - 功能测试结果
- **更新日志**: [更新日志.md](./更新日志.md) - 版本历史和改进
- **完整文档**: 继续阅读本文档

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

#### Claude Code (CLI) - 推荐方法

使用 Claude Code 内置的 MCP 管理命令:

##### 用户级配置(推荐)

```bash
claude mcp add -s user wechat-search \
  "/Users/rick/Documents/AI产品开发/微信文章搜索摘要MCP/.venv/bin/python" \
  "/Users/rick/Documents/AI产品开发/微信文章搜索摘要MCP/mcp_server.py"
```

**验证配置**:
```bash
claude mcp list
# 应该看到: wechat-search: /path/to/python /path/to/mcp_server.py
```

**说明**:
- 用户级配置在所有项目中生效
- 使用虚拟环境的 Python,确保依赖已安装
- 必须使用绝对路径

##### 项目级配置

如果只想在特定项目中使用,在项目目录下:

```bash
cd ~/my-project
claude mcp add -s project wechat-search \
  "/Users/rick/Documents/AI产品开发/微信文章搜索摘要MCP/.venv/bin/python" \
  "/Users/rick/Documents/AI产品开发/微信文章搜索摘要MCP/mcp_server.py"
```

##### 其他有用命令

```bash
# 列出所有 MCP 服务器
claude mcp list

# 查看特定服务器详情
claude mcp get wechat-search

# 删除 MCP 服务器
claude mcp remove -s user wechat-search
```

### 3. 启动 Claude Code

在任意目录打开终端:

```bash
# 直接启动 Claude Code
claude

# 或指定工作目录
claude /path/to/your/project
```

Claude Code 启动时会自动加载 MCP 配置,你会在启动信息中看到:

```
✓ Connected to MCP server wechat-search
```

### 4. 验证 MCP 已加载

在 Claude Code 中输入:

```
> 列出可用的工具
```

或直接测试:

```
> 搜索关于AI的微信文章
```

如果 MCP 正常工作,Claude 会自动调用 `search_wechat_articles` 工具。

## 💡 使用示例

### 在 Claude Code 中使用

#### 第一步:启动 Claude Code

```bash
# 在终端启动
claude

# 或在特定目录启动
cd ~/my-project
claude
```

#### 第二步:自然语言调用

Claude Code 会自动识别何时需要调用 MCP 工具,你只需要用自然语言描述需求:

##### 示例 1: 基础搜索

```
> 搜索关于人工智能的微信文章
```

Claude 会:
1. 自动调用 `search_wechat_articles("人工智能", count=3)`
2. 获取 3 篇文章的完整内容
3. 分析并返回总结

##### 示例 2: 指定文章数量

```
> 搜索关于"大模型应用"的微信文章,获取 5 篇
```

Claude 会搜索 5 篇文章并分析。

##### 示例 3: 带分析角度

```
> 搜索关于区块链技术的文章,从监管角度分析
```

Claude 会获取文章后,专门从监管角度进行分析。

##### 示例 4: 多轮对话

```
> 搜索关于Claude MCP的文章

[Claude 返回搜索结果和分析]

> 这些文章主要讨论了哪些应用场景?

[Claude 基于已获取的内容深入分析]

> 第二篇文章的公众号是什么?

[Claude 直接从结果中提取信息]
```

#### 第三步:查看结果

Claude 会返回类似这样的内容:

```markdown
根据搜索到的 3 篇微信文章,我为你总结如下:

## 主要观点
1. [总结要点1]
2. [总结要点2]
...

## 文章来源
1. **标题**: XXX
   - 公众号: XXX
   - 链接: https://mp.weixin.qq.com/...
   
2. **标题**: YYY
   - 公众号: YYY
   - 链接: https://mp.weixin.qq.com/...
```

你可以:
- 点击链接查看原文
- 继续追问细节
- 要求从不同角度分析

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

#### 检查配置文件

1. **验证配置文件位置**

   项目级配置:
   ```bash
   # 检查当前目录是否有 CLAUDE.md
   ls -la CLAUDE.md
   ```

   全局配置:
   ```bash
   # 检查全局配置文件
   cat ~/.config/claude/settings.json
   ```

2. **验证路径是否正确**

   ```bash
   # 测试 Python 路径
   /Users/rick/Documents/AI产品开发/微信文章搜索摘要MCP/.venv/bin/python --version
   
   # 测试脚本路径
   ls -la "/Users/rick/Documents/AI产品开发/微信文章搜索摘要MCP/mcp_server.py"
   ```

3. **检查依赖是否安装**

   ```bash
   cd "/Users/rick/Documents/AI产品开发/微信文章搜索摘要MCP"
   .venv/bin/pip list | grep -E "mcp|httpx|lxml"
   ```

   应该看到:
   ```
   httpx          0.28.1
   lxml           6.0.2
   mcp            1.20.0
   ```

#### 查看 Claude Code 日志

启动 Claude Code 时观察输出:

```bash
claude

# 正常情况应该看到:
# ✓ Connected to MCP server wechat-search
```

如果看到错误信息,根据提示修复。

#### 手动测试 MCP 服务

```bash
cd "/Users/rick/Documents/AI产品开发/微信文章搜索摘要MCP"
.venv/bin/python mcp_server.py
```

如果有错误会立即显示。按 Ctrl+C 退出。

### 搜索无结果

- 尝试更换关键词
- 检查网络连接
- 可能被搜狗反爬虫拦截,稍后重试

### 文章内容抓取失败

✅ **v1.1更新**: 已改进URL提取算法,文章内容抓取成功率大幅提升!

参考了 [fancyboi999/weixin_search_mcp](https://github.com/fancyboi999/weixin_search_mcp) 项目的实现方法:
- 从JavaScript代码中提取URL片段并拼接
- 增强HTTP请求头模拟真实浏览器
- 传递Referer链路追踪

如仍遇到抓取失败:
- 可能是反爬虫临时拦截,稍后重试
- MCP 仍会返回文章标题、公众号、摘要和链接
- 用户可通过链接手动访问原文

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
