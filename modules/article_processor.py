import httpx
from lxml import html
import asyncio
from typing import List, Dict
import config
import re


class ArticleProcessor:
    
    @staticmethod
    async def fetch_all(search_results: List[Dict[str, str]]) -> List[Dict[str, str]]:
        semaphore = asyncio.Semaphore(config.MAX_CONCURRENT_FETCHES)
        
        async def fetch_with_semaphore(article: Dict[str, str]) -> Dict[str, str]:
            async with semaphore:
                referer = article.get('sogou_url', '')
                content = await ArticleProcessor._fetch_single(article['url'], referer=referer)
                return {
                    'title': article['title'],
                    'url': article['url'],
                    'gzh_name': article['gzh_name'],
                    'abstract': article['abstract'],
                    'content': content
                }
        
        tasks = [fetch_with_semaphore(article) for article in search_results]
        articles = await asyncio.gather(*tasks, return_exceptions=True)
        
        valid_articles = []
        for article in articles:
            if isinstance(article, Exception):
                print(f"抓取文章失败: {article}")
                continue
            if article['content']:
                valid_articles.append(article)
        
        return valid_articles
    
    @staticmethod
    async def _fetch_single(url: str, referer: str = None) -> str:
        headers = {
            "User-Agent": config.USER_AGENT,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
            "Cache-Control": "no-cache",
            "Pragma": "no-cache",
        }
        
        if referer:
            headers["Referer"] = referer
        
        try:
            async with httpx.AsyncClient(timeout=config.REQUEST_TIMEOUT, follow_redirects=True) as client:
                response = await client.get(url, headers=headers)
                response.raise_for_status()
                
                tree = html.fromstring(response.text)
                
                content_elem = tree.xpath('//div[@id="js_content"]')
                if not content_elem:
                    content_elem = tree.xpath('//div[@class="rich_media_content"]')
                
                if content_elem:
                    content_html = content_elem[0]
                    
                    for elem in content_html.xpath('.//script | .//style'):
                        elem.getparent().remove(elem)
                    
                    text_parts = []
                    for elem in content_html.xpath('.//p | .//div | .//span | .//h1 | .//h2 | .//h3 | .//section'):
                        text = elem.text_content().strip()
                        if text and len(text) > 10:
                            text_parts.append(text)
                    
                    full_text = '\n\n'.join(text_parts)
                    
                    full_text = re.sub(r'\n{3,}', '\n\n', full_text)
                    
                    if len(full_text) > config.MAX_ARTICLE_LENGTH:
                        full_text = full_text[:config.MAX_ARTICLE_LENGTH] + "\n\n...(内容过长已截断)"
                    
                    return full_text
                
                return "无法提取文章内容"
                
        except httpx.TimeoutException:
            return "文章抓取超时"
        except httpx.HTTPStatusError as e:
            return f"文章抓取失败: HTTP {e.response.status_code}"
        except Exception as e:
            return f"文章解析失败: {str(e)}"
