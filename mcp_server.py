#!/usr/bin/env python3
import asyncio
from mcp.server.fastmcp import FastMCP
from modules.weixin_search import WeixinSearch
from modules.article_processor import ArticleProcessor
import config

mcp = FastMCP("wechat-search")


@mcp.tool()
async def search_wechat_articles(query: str, count: int = config.DEFAULT_ARTICLE_COUNT) -> str:
    """搜索微信公众号文章并返回完整内容
    
    搜索微信公众号文章,自动抓取文章完整正文内容。返回的内容将由调用的 LLM 
    根据用户问题进行智能分析和总结。
    
    Args:
        query: 搜索关键词或自然语言描述
        count: 获取文章数量,默认 3 篇,范围 1-10
    
    Returns:
        包含所有文章完整内容的 Markdown 格式文本
    """
    
    if count < 1:
        count = 1
    if count > config.MAX_ARTICLE_COUNT:
        count = config.MAX_ARTICLE_COUNT
    
    try:
        search_results = await WeixinSearch.search(query, num=count)
        
        if not search_results:
            return f"❌ 未找到关于「{query}」的相关文章,请尝试其他关键词。"
        
        articles = await ArticleProcessor.fetch_all(search_results)
        
        if not articles:
            return f"❌ 搜索到文章但无法获取内容,可能被反爬虫拦截,请稍后重试。"
        
        output = f"# 微信文章搜索结果\n\n"
        output += f"**搜索关键词**: {query}\n"
        output += f"**找到文章数**: {len(articles)}\n\n"
        output += "---\n\n"
        
        for i, article in enumerate(articles, 1):
            output += f"## 文章 {i}: {article['title']}\n\n"
            output += f"**公众号**: {article['gzh_name']}\n"
            output += f"**链接**: {article['url']}\n\n"
            
            if article['abstract']:
                output += f"**摘要**: {article['abstract']}\n\n"
            
            output += f"### 正文内容\n\n"
            output += f"{article['content']}\n\n"
            output += "---\n\n"
        
        return output
        
    except Exception as e:
        return f"❌ 搜索过程中出错: {str(e)}"


if __name__ == "__main__":
    mcp.run()
