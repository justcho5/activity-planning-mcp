from fastmcp import FastMCP
from . import config
from functools import lru_cache
from typing import Optional

mcp = FastMCP()


@mcp.tool
def get_events_by_date(
    city: str, start_date: str, end_date: str, keyword: Optional[str] = None
):
    pass
