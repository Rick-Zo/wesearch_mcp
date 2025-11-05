# 微信公众号文章搜索与总结 MCP 开发方案 (v2.0)

**作者**: Manus AI  
**日期**: 2025 年 11 月 5 日  
**版本**: 2.0

---

## 执行摘要

本文档为现有微信公众号文章总结 MCP 的升级提供完整的技术方案。新版本将引入**主动搜索功能**,允许 MCP 根据用户在对话中的自然语言描述,自动提取关键词,在搜狗微信搜索中查找相关文章,并对搜索结果进行批量处理和总结。该方案旨在将 MCP 从一个被动的链接处理工具,升级为一个具备主动信息获取和整合能力的智能助手。

---

## 一、项目背景与目标

### 1.1 项目背景

在 v1.0 版本中,我们实现了一个接收文章链接并生成总结的 MCP 工具。为了进一步提升其智能化水平和实用性,我们计划引入主动搜索功能。用户不再需要手动寻找并提供文章链接,只需描述其信息需求,MCP 即可自动完成搜索、筛选、阅读和总结的全过程。

### 1.2 升级目标

本次升级的核心目标是为 MCP 增加以下能力:

1.  **关键词提取**: 从用户的自然语言描述中,利用大语言模型 (LLM) 自动提取核心搜索关键词。
2.  **微信文章搜索**: 调用搜狗微信搜索接口,根据关键词查找相关文章。
3.  **可配置文章获取**: 默认获取搜索结果的前 3 篇文章,并支持用户配置获取数量 (最多 10 篇)。
4.  **批量内容处理**: 并发抓取多篇文章的标题、链接、摘要和正文内容。
5.  **综合信息输出**: 
    - 生成一份对所有搜索文章内容的**综合总结**。
    - 提供一个包含公众号名称、标题、链接和原文摘要的**文章列表**。

### 1.3 适用场景

升级后的 MCP 将适用于更广泛的场景:

- **即时研究**: 快速调研某一主题在微信公众号上的相关讨论和观点。
- **舆情监控**: 搜索特定关键词,了解相关事件的最新动态和舆论反馈。
- **内容发现**: 根据兴趣点自动发现和筛选高质量的公众号文章。

---

## 二、技术选型与架构设计

### 2.1 技术栈选择

技术栈保持与 v1.0 一致,并引入异步处理以提高批量抓取效率。

| **模块** | **技术/库** | **版本要求** | **选型理由** |
|---|---|---|---|
| MCP 服务端框架 | `mcp` (FastMCP) | ≥ 1.2.0 | 官方推荐,开发效率高 |
| HTTP 请求 | `httpx` | ≥ 0.23.0 | 支持异步请求,适合并发抓取 |
| HTML 解析 | `lxml` | ≥ 4.9.0 | 高性能的 XPath 解析器,用于精确提取页面元素 |
| AI 模型调用 | `zhipuai` | 最新版 | 智谱 AI 官方 SDK,用于关键词提取和内容总结 |

### 2.2 系统架构 (v2.0)

系统架构将进行重构,以支持新的主动搜索工作流。

#### 架构图

```
┌─────────────────────────────────────────────────────────────┐
│                      MCP Host (客户端)                        │
└─────────────────────┬───────────────────────────────────────┘
                      │ JSON-RPC 2.0 (STDIO)
                      ↓
┌─────────────────────────────────────────────────────────────┐
│                    MCP Server (服务端)                        │
│                    mcp_server.py                             │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  @mcp.tool()                                          │  │
│  │  search_and_summarize(query: str, count: int) -> str │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────┬───────────────────────────────────────┘
                      │
        ┌─────────────┴─────────────┬───────────────────────────┐
        ↓                           ↓                           ↓
┌───────────────────┐       ┌───────────────────┐       ┌───────────────────┐
│ 关键词提取模块    │       │  微信搜索模块      │       │  文章处理模块      │
│ modules/          │       │  modules/         │       │  modules/         │
│ └─ keyword_ext.py│       │  └─ weixin_search.py│      │  └─ article_proc.py│
└───────────────────┘       └───────────────────┘       └───────────────────┘
        │                           │                           │
        ↓                           ↓                           ↓
┌───────────────────┐       ┌───────────────────┐       ┌───────────────────┐
│  智谱 AI API      │       │  搜狗微信搜索      │       │  微信公众号服务器  │
│  (GLM-4)          │       │  (搜索结果页)      │       │  (文章页面)        │
└───────────────────┘       └───────────────────┘       └───────────────────┘
```

#### 模块职责

1.  **MCP Server (`mcp_server.py`)**
    -   定义新的 MCP 工具 `search_and_summarize`,接收 `query` (用户描述) 和 `count` (文章数量) 参数。
    -   作为总控制器,依次调用关键词提取、微信搜索和文章处理模块。

2.  **关键词提取模块 (`modules/keyword_extractor.py`)**
    -   接收用户输入,构建 Prompt 调用 GLM-4 提取 1-3 个核心关键词。

3.  **微信搜索模块 (`modules/weixin_search.py`)**
    -   参考 `fancyboi999/weixin_search_mcp` 项目的实现,直接请求搜狗微信搜索页面。
    -   使用 `httpx` 和 `lxml` 解析搜索结果页,提取文章的标题、临时链接、公众号名称和摘要。
    -   处理反爬虫机制,如设置 `User-Agent`、处理 Cookie 等。
    -   **关键实现**: 包含一个解析搜狗跳转链接以获取真实微信文章 URL 的函数。

4.  **文章处理模块 (`modules/article_processor.py`)**
    -   接收文章 URL 列表,使用 `asyncio` 和 `httpx` 并发抓取所有文章的 HTML 内容。
    -   对每篇文章,解析并提取干净的正文。
    -   将所有文章的正文拼接在一起,构建 Prompt 调用 GLM-4 生成**综合总结**。
    -   格式化文章列表,包含公众号名、标题、真实链接和摘要。

### 2.3 数据流程 (v2.0)

1.  用户在客户端调用 `search_and_summarize` 工具,传入自然语言描述。
2.  MCP Server 将描述传递给 `keyword_extractor.py`,获取搜索关键词。
3.  关键词传递给 `weixin_search.py`,获取搜索结果列表 (包含临时链接)。
4.  搜索结果列表传递给 `article_processor.py`。
5.  `article_processor.py` 并发抓取和解析所有文章,获取正文和元数据。
6.  所有文章正文被合并,传递给 GLM-4 生成综合总结。
7.  `article_processor.py` 将综合总结和格式化的文章列表返回给 MCP Server。
8.  MCP Server 将最终结果以 Markdown 格式返回给客户端。

---

## 三、详细实现方案

### 3.1 项目目录结构 (v2.0)

```
wechat-mcp-summarizer/
├── .venv/
├── mcp_server.py           # MCP 服务端主程序
├── modules/
│   ├── __init__.py
│   ├── keyword_extractor.py  # 关键词提取模块
│   ├── weixin_search.py      # 微信搜索模块
│   └── article_processor.py  # 文章批量处理模块
├── config.py
├── requirements.txt
├── .env.example
└── README.md
```

### 3.2 核心代码实现 (伪代码)

#### `mcp_server.py`

```python
@mcp.tool()
async def search_and_summarize(query: str, count: int = 3) -> str:
    # 1. 提取关键词
    keywords = await KeywordExtractor.extract(query)
    
    # 2. 搜索文章
    search_results = await WechatSearch.search(keywords, num=count)
    if not search_results:
        return "❌ 未找到相关文章。"

    # 3. 处理文章并总结
    summary, article_list = await ArticleProcessor.process(search_results)
    
    # 4. 格式化输出
    output = f"# 搜索总结\n\n{summary}\n\n## 文章列表\n\n"
    for article in article_list:
        output += f"### {article['title']}\n"
        output += f"- **公众号**: {article['gzh_name']}\n"
        output += f"- **链接**: {article['real_url']}\n"
        output += f"- **摘要**: {article['abstract']}\n\n"
    return output
```

#### `modules/weixin_search.py`

```python
class WechatSearch:
    async def search(keywords: str, num: int):
        # 构造搜狗搜索 URL
        search_url = f"https://weixin.sogou.com/weixin?type=2&query={keywords}"
        
        # 使用 httpx 请求
        async with httpx.AsyncClient() as client:
            response = await client.get(search_url, headers=...)
        
        # 使用 lxml 解析 HTML
        tree = html.fromstring(response.text)
        articles = tree.xpath('//ul[@class="news-list"]/li')
        
        results = []
        for article_node in articles[:num]:
            title = article_node.xpath('.//h3/a')[0].text_content()
            sogou_url = article_node.xpath('.//h3/a')[0].get('href')
            gzh_name = article_node.xpath('.//a[@class="account"]')[0].text_content()
            abstract = article_node.xpath('.//p[contains(@class, "txt-info")]')[0].text_content()
            
            # 获取真实链接
            real_url = await self.get_real_url(sogou_url)
            
            results.append({
                'title': title,
                'real_url': real_url,
                'gzh_name': gzh_name,
                'abstract': abstract
            })
        return results

    async def get_real_url(sogou_url: str) -> str:
        # 请求搜狗的跳转链接,从返回的脚本中用正则表达式提取真实 URL
        # ... 实现参考 fancyboi999/weixin_search_mcp
        pass
```

#### `modules/article_processor.py`

```python
class ArticleProcessor:
    async def process(search_results: list):
        # 并发抓取所有文章
        tasks = [self.fetch_and_parse(article['real_url']) for article in search_results]
        contents = await asyncio.gather(*tasks)
        
        # 合并内容并生成总结
        full_text = "\n\n---\n\n".join(contents)
        summary_prompt = f"请根据以下多篇文章内容,生成一份综合性总结:\n\n{full_text}"
        summary = await ZhipuAI_Client.chat.completions.create(..., messages=[...])
        
        # 准备文章列表
        article_list = search_results
        
        return summary.choices[0].message.content, article_list

    async def fetch_and_parse(url: str) -> str:
        # 抓取并解析单个文章,返回纯文本内容
        # ... 实现与 v1.0 类似
        pass
```

---

## 四、风险评估与缓解措施

### 4.1 技术风险

-   **搜狗反爬升级**: 搜狗微信搜索随时可能更新其前端页面结构或增加反爬虫措施,导致 `weixin_search.py` 模块失效。
    -   **缓解措施**: 
        1.  在代码中增加详细的错误处理和日志记录,一旦解析失败立即告警。
        2.  准备备用方案,如集成第三方商业 API 或其他开源爬虫库。
        3.  设计灵活的解析规则,使其能够适应微小的页面变化。

-   **IP 封禁**: 频繁的搜索和抓取请求可能导致服务器 IP 被搜狗或微信封禁。
    -   **缓解措施**: 
        1.  在 `httpx` 客户端中配置代理,使用代理 IP 池进行请求。
        2.  在请求之间设置合理的随机延迟,模拟人类行为。
        3.  限制用户可配置的最大文章数量,避免单次请求过于庞大。

### 4.2 法律与合规风险

-   **版权问题**: 抓取和展示文章内容可能涉及版权侵犯。
    -   **缓解措施**: 
        1.  明确工具仅供个人学习和研究使用。
        2.  在输出结果中始终包含原文链接,引导用户阅读原文。
        3.  生成的总结属于衍生作品,但仍需谨慎使用。

-   **服务条款**: 爬虫行为可能违反搜狗和微信的服务条款 (ToS)。
    -   **缓解措施**: 
        1.  遵循 `robots.txt` 协议 (虽然对于 API 驱动的工具可能不完全适用)。
        2.  将工具的使用限制在合理范围内,避免对目标服务器造成过大负担。


### 4.3 性能风险

-   **GLM-4 API 调用成本**: 每次搜索可能需要调用 GLM-4 两次 (关键词提取 + 综合总结),且总结的输入 token 数量可能较大。
    -   **缓解措施**: 
        1.  在 `config.py` 中设置 `max_tokens` 参数,限制每篇文章的最大长度。
        2.  对超长文章进行截断,只保留前 N 个字符。
        3.  提供配置选项,允许用户选择是否生成综合总结,或仅返回文章列表。

-   **并发抓取性能**: 同时抓取 10 篇文章可能导致网络拥塞或超时。
    -   **缓解措施**: 
        1.  使用 `asyncio.Semaphore` 限制并发数量,如最多同时抓取 3 篇文章。
        2.  为每个请求设置合理的超时时间 (如 30 秒)。
        3.  对失败的请求进行重试,但限制重试次数。

---

## 五、开发步骤与时间估算

### 5.1 开发步骤

1.  **环境搭建** (1 小时)
    -   创建 Python 虚拟环境。
    -   安装依赖: `httpx`, `lxml`, `zhipuai`, `mcp`。
    -   配置 `config.py` 和 `.env` 文件。

2.  **关键词提取模块开发** (2 小时)
    -   实现 `keyword_extractor.py`。
    -   设计 Prompt 模板,确保提取的关键词准确且简洁。
    -   编写单元测试,验证不同输入下的提取效果。

3.  **微信搜索模块开发** (6 小时)
    -   参考 `fancyboi999/weixin_search_mcp` 项目,实现 `weixin_search.py`。
    -   重点实现搜索结果页的解析和真实链接的提取。
    -   处理反爬虫措施,如验证码、Cookie 管理等。
    -   测试不同关键词下的搜索结果准确性。

4.  **文章处理模块开发** (4 小时)
    -   实现 `article_processor.py`,包括并发抓取和解析逻辑。
    -   实现综合总结的 Prompt 构建和 GLM-4 调用。
    -   测试并发抓取的性能和稳定性。

5.  **MCP Server 集成** (2 小时)
    -   在 `mcp_server.py` 中定义 `search_and_summarize` 工具。
    -   集成所有模块,实现完整的数据流。
    -   添加错误处理和日志记录。

6.  **测试与调优** (3 小时)
    -   端到端测试,模拟用户真实使用场景。
    -   测试边界情况,如无搜索结果、网络超时、API 限流等。
    -   根据测试结果调整参数和逻辑。

7.  **文档编写** (2 小时)
    -   编写 `README.md`,包括安装、配置和使用说明。
    -   编写代码注释,提高可维护性。

### 5.2 总时间估算

**总计**: 约 20 小时 (2.5 个工作日)

---

## 六、配置与部署

### 6.1 依赖安装

在项目根目录下创建 `requirements.txt`:

```
mcp>=1.2.0
httpx>=0.23.0
lxml>=4.9.0
zhipuai
```

安装依赖:

```bash
# 创建虚拟环境
python3 -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt
```

### 6.2 配置文件

创建 `config.py`:

```python
import os

# 智谱 AI API Key
ZHIPUAI_API_KEY = os.getenv("ZHIPUAI_API_KEY", "your_api_key_here")

# 默认获取文章数量
DEFAULT_ARTICLE_COUNT = 3

# 最大获取文章数量
MAX_ARTICLE_COUNT = 10

# 每篇文章的最大字符数 (用于截断)
MAX_ARTICLE_LENGTH = 5000

# 并发抓取的最大数量
MAX_CONCURRENT_FETCHES = 3

# 请求超时时间 (秒)
REQUEST_TIMEOUT = 30

# User-Agent
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
```

创建 `.env.example`:

```
ZHIPUAI_API_KEY=your_api_key_here
```

### 6.3 启动服务

在项目根目录下运行:

```bash
python mcp_server.py
```

或者使用 `uvx` (如果已安装):

```bash
uvx --from . mcp_server
```

### 6.4 集成到 MCP 客户端

以 Claude for Desktop 为例,在配置文件中添加:

```json
{
  "mcpServers": {
    "wechat_summarizer": {
      "command": "python",
      "args": ["/path/to/wechat-mcp-summarizer/mcp_server.py"],
      "env": {
        "ZHIPUAI_API_KEY": "your_api_key_here"
      }
    }
  }
}
```

---

## 七、使用示例

### 7.1 基本使用

用户在 Claude for Desktop 中输入:

> "帮我搜索一下关于人工智能在医疗领域应用的微信文章"

MCP 自动执行:

1.  提取关键词: "人工智能 医疗"
2.  在搜狗微信搜索中查找相关文章
3.  获取前 3 篇文章的内容
4.  生成综合总结和文章列表

### 7.2 自定义文章数量

用户可以指定获取的文章数量:

> "搜索关于'区块链技术'的微信文章,获取 5 篇"

MCP 将获取前 5 篇文章进行处理。

### 7.3 输出示例

```markdown
# 搜索总结

## 综合总结

根据搜索到的文章,人工智能在医疗领域的应用主要集中在以下几个方面:

首先,**医学影像诊断**是 AI 应用最成熟的领域之一。深度学习算法能够快速准确地识别 CT、MRI 等影像中的病灶,辅助医生进行早期诊断。多篇文章提到,AI 在肺癌、乳腺癌等疾病的影像诊断中已达到甚至超越人类专家的水平。

其次,**药物研发**也是 AI 的重要应用场景。传统药物研发周期长、成本高,而 AI 可以通过分析海量生物数据,预测药物分子的活性和毒性,大幅缩短研发时间。文章中提到,多家制药公司已将 AI 技术应用于新药筛选和临床试验设计。

此外,**个性化医疗**和**健康管理**也是 AI 的新兴应用方向。通过分析患者的基因组数据、病史和生活习惯,AI 可以为每位患者制定个性化的治疗方案和健康建议。

然而,文章也指出了 AI 在医疗领域面临的挑战,包括数据隐私保护、算法的可解释性、以及医疗责任的界定等问题。

## 文章列表

### 1. AI 赋能医疗:从影像诊断到精准治疗

-   **公众号**: 健康科技前沿
-   **链接**: https://mp.weixin.qq.com/s/xxxxx
-   **摘要**: 本文介绍了人工智能在医学影像诊断、药物研发和精准医疗等领域的最新进展,并探讨了 AI 技术在医疗行业的未来发展趋势。

### 2. 深度学习如何改变医疗行业?

-   **公众号**: AI 观察
-   **链接**: https://mp.weixin.qq.com/s/yyyyy
-   **摘要**: 文章详细分析了深度学习技术在医疗影像分析、疾病预测和个性化治疗中的应用案例,并讨论了技术落地过程中的挑战。

### 3. 人工智能与医疗:机遇与挑战并存

-   **公众号**: 医疗创新
-   **链接**: https://mp.weixin.qq.com/s/zzzzz
-   **摘要**: 本文从政策、技术和伦理三个维度,探讨了人工智能在医疗领域的机遇和挑战,强调了数据安全和算法透明度的重要性。
```

---

## 八、优化建议与未来扩展

### 8.1 短期优化 (1-2 周)

1.  **缓存机制**: 对搜索结果和文章内容实现本地缓存,避免重复抓取相同的文章。
2.  **结果排序**: 引入文章质量评分机制,如根据阅读量、点赞数等指标对搜索结果进行排序。
3.  **错误重试**: 对网络请求失败的情况实现自动重试,提高系统鲁棒性。

### 8.2 中期扩展 (1-2 个月)

1.  **多源搜索**: 除了搜狗微信搜索,还可以集成其他搜索引擎或 API,如知乎、微博等。
2.  **时间过滤**: 允许用户指定搜索文章的发布时间范围,如"最近一周"、"最近一个月"等。
3.  **主题分类**: 对搜索到的文章进行自动分类,如"技术"、"政策"、"案例"等。

### 8.3 长期愿景 (3-6 个月)

1.  **知识图谱构建**: 将多次搜索的结果整合成知识图谱,帮助用户建立系统化的知识体系。
2.  **订阅与监控**: 允许用户订阅特定关键词,定期自动搜索并推送最新文章。
3.  **多模态支持**: 支持处理文章中的图片、视频等多媒体内容,提供更全面的总结。

---

## 九、参考资料

本方案的设计参考了以下开源项目和技术文档:

1.  **Model Context Protocol (MCP) 官方文档**  
    [https://modelcontextprotocol.io/](https://modelcontextprotocol.io/)  
    提供了 MCP 协议的完整规范和 Python SDK 的使用指南。

2.  **fancyboi999/weixin_search_mcp**  
    [https://github.com/fancyboi999/weixin_search_mcp](https://github.com/fancyboi999/weixin_search_mcp)  
    一个已实现的微信搜索 MCP 项目,提供了搜狗微信搜索的解析逻辑和真实链接提取方法。

3.  **chyroc/WechatSogou**  
    [https://github.com/chyroc/WechatSogou](https://github.com/chyroc/WechatSogou)  
    一个成熟的微信公众号爬虫库,提供了丰富的搜索和解析功能,虽然项目较旧,但仍有参考价值。

4.  **智谱 AI GLM-4 API 文档**  
    [https://open.bigmodel.cn/dev/api](https://open.bigmodel.cn/dev/api)  
    智谱 AI 官方 API 文档,提供了 GLM-4 模型的调用方法和参数说明。

---

## 十、总结

本开发方案为微信公众号文章总结 MCP 的 v2.0 升级提供了完整的技术路线图。通过引入关键词提取和主动搜索功能,该工具将从一个被动的链接处理器,升级为一个具备主动信息获取和整合能力的智能助手。方案中详细描述了系统架构、模块设计、代码实现、风险评估和优化建议,为开发者提供了清晰的指导。

在实施过程中,需要特别关注搜狗反爬虫机制的应对、并发性能的优化、以及 GLM-4 API 调用成本的控制。同时,也要注意遵守相关法律法规,确保工具仅用于个人学习和研究目的。

通过本次升级,MCP 将能够更好地满足用户在信息获取、内容筛选和知识管理方面的需求,为构建更智能、更高效的 AI 工作流奠定基础。
