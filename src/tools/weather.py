"""
自定义工具：天气查询
====================

使用 @tool 装饰器创建工具（LangChain 1.0 推荐方式）
"""

from typing import Optional

from langchain_core.tools import BaseTool, tool
from pydantic import BaseModel, Field


class WeatherArg(BaseModel):
    city: str


@tool
def get_weather(city: str) -> str:
    """
    获取指定城市的天气信息

    参数:
        city: 城市名称，如"北京"、"上海"

    返回:
        天气信息字符串
    """
    # 模拟天气数据（实际应用中应调用真实API）
    weather_data = {
        "北京": "晴天，温度 15°C，空气质量良好",
        "上海": "多云，温度 18°C，有轻微雾霾",
        "深圳": "阴天，温度 22°C，可能有小雨",
        "成都": "小雨，温度 12°C，湿度较高",
    }

    return weather_data.get(city, f"抱歉，暂时没有{city}的天气数据")


class WeatherTool(BaseTool):
    name: str = "get_weather"
    description: str = "获取指定城市的天气信息"

    weather_url: str = Field(default="http://api.weather.com/v1/city")

    def __init__(self, weather_url: Optional[str] = None):
        super().__init__()
        if weather_url:
            self.weather_url = weather_url

    def _run(self, city: str) -> str:
        weather_data = {
            "北京": "晴天，温度 15°C，空气质量良好",
            "上海": "多云，温度 18°C，有轻微雾霾",
            "深圳": "阴天，温度 22°C，可能有小雨",
            "成都": "小雨，温度 12°C，湿度较高",
        }
        return weather_data.get(city, f"抱歉，暂时没有{city}的天气数据")


# 测试工具
if __name__ == "__main__":
    print("测试天气工具：")
    weather_tool = WeatherTool()
    for city in ["北京", "上海", "深圳", "成都", "未知城市"]:
        arg = WeatherArg(city=city)
        print(f"@tool    {city}, response: {get_weather.invoke(arg.model_dump())}")
        print(f"BaseTool {city}, response: {weather_tool.invoke(arg.model_dump())}")
