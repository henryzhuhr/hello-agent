from enum import StrEnum


class StockMarket(StrEnum):
    """股票市场"""

    SH = "SH"  # 上海证券交易所
    SZ = "SZ"  # 深圳证券交易所
    HK = "HK"  # 香港联合交易所
    US = "US"  # 美国证券交易所
