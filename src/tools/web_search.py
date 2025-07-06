"""
Web search tool for AI Agent
"""
import aiohttp
import asyncio
from typing import Dict, Any, List, Optional
from bs4 import BeautifulSoup
import requests
from .base_tool import BaseTool, ToolResult

class WebSearchTool(BaseTool):
    """Tool for searching the web and extracting information"""
    
    def __init__(self):
        super().__init__(
            name="web_search",
            description="Search the web for information on any topic"
        )
    
    async def execute(self, query: str, num_results: int = 3) -> ToolResult:
        """
        Execute web search
        
        Args:
            query: Search query
            num_results: Number of results to return
            
        Returns:
            ToolResult with search results
        """
        try:
            # Use DuckDuckGo search (no API key required)
            search_results = await self._search_duckduckgo(query, num_results)
            
            if not search_results:
                return ToolResult(
                    success=False,
                    result=None,
                    error="No search results found"
                )
            
            return ToolResult(
                success=True,
                result={
                    "query": query,
                    "results": search_results,
                    "num_results": len(search_results)
                },
                metadata={"source": "duckduckgo"}
            )
            
        except Exception as e:
            return ToolResult(
                success=False,
                result=None,
                error=f"Web search failed: {str(e)}"
            )
    
    async def _search_duckduckgo(self, query: str, num_results: int) -> List[Dict[str, str]]:
        """
        Search using DuckDuckGo
        
        Args:
            query: Search query
            num_results: Number of results
            
        Returns:
            List of search results
        """
        try:
            # DuckDuckGo instant answer API
            async with aiohttp.ClientSession() as session:
                params = {
                    'q': query,
                    'format': 'json',
                    'no_redirect': '1',
                    'no_html': '1',
                    'skip_disambig': '1'
                }
                
                async with session.get(
                    'https://api.duckduckgo.com/',
                    params=params
                ) as response:
                    data = await response.json()
                    
                    results = []
                    
                    # Add abstract if available
                    if data.get('Abstract'):
                        results.append({
                            'title': data.get('AbstractText', 'Abstract'),
                            'snippet': data.get('Abstract'),
                            'url': data.get('AbstractURL', ''),
                            'source': data.get('AbstractSource', 'DuckDuckGo')
                        })
                    
                    # Add related topics
                    for topic in data.get('RelatedTopics', [])[:num_results-1]:
                        if isinstance(topic, dict) and 'Text' in topic:
                            results.append({
                                'title': topic.get('FirstURL', '').split('/')[-1].replace('_', ' '),
                                'snippet': topic.get('Text'),
                                'url': topic.get('FirstURL', ''),
                                'source': 'DuckDuckGo'
                            })
                    
                    return results[:num_results]
                    
        except Exception as e:
            # Fallback to simple web scraping
            return await self._simple_web_search(query, num_results)
    
    async def _simple_web_search(self, query: str, num_results: int) -> List[Dict[str, str]]:
        """
        Simple web search fallback
        
        Args:
            query: Search query
            num_results: Number of results
            
        Returns:
            List of search results
        """
        try:
            # This is a simplified implementation
            # In production, you might want to use proper search APIs
            search_url = f"https://duckduckgo.com/html/?q={query}"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(search_url, headers=headers, timeout=10) as response:
                    content = await response.text()
                    soup = BeautifulSoup(content, 'html.parser')
                    
                    results = []
                    result_divs = soup.find_all('div', class_='result')[:num_results]
                    
                    for div in result_divs:
                        title_elem = div.find('a', class_='result__a')
                        snippet_elem = div.find('a', class_='result__snippet')
                        
                        if title_elem:
                            title = title_elem.get_text(strip=True)
                            url = title_elem.get('href', '')
                            snippet = snippet_elem.get_text(strip=True) if snippet_elem else ''
                            
                            results.append({
                                'title': title,
                                'snippet': snippet,
                                'url': url,
                                'source': 'DuckDuckGo'
                            })
                    
                    return results
            
        except Exception:
            return []
    
    def get_parameters_schema(self) -> Dict[str, Any]:
        """Get parameters schema for web search tool"""
        return {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The search query to look for on the web"
                },
                "num_results": {
                    "type": "integer",
                    "description": "Number of search results to return (default: 3, max: 10)",
                    "minimum": 1,
                    "maximum": 10,
                    "default": 3
                }
            },
            "required": ["query"]
        }
