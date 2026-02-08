"""
搜索股票的接口
"""

from abc import ABC, abstractmethod
from typing import List

from pydantic import BaseModel, Field

from src.stock.types.market import StockMarket


class StockInfo(BaseModel):
    market: StockMarket = Field(..., description="股票市场")
    code: str = Field(..., description="股票代码")
    name: str = Field(..., description="股票名称")
    abbreviation: str = Field(default="", description="股票简称")


class BaseStockSearcher(ABC):
    """股票代码搜索器基类，定义接口"""

    @abstractmethod
    def search_stock_list(self, keyword: str) -> List[StockInfo]:
        raise NotImplementedError("Subclasses must implement search_stock_list method")
