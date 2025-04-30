"""值对象单元测试"""

import pytest
from datetime import datetime
from src.domain.model.value_objects import (
    Season, Weather, Occasion,
    SeasonEnum, WeatherEnum, OccasionEnum
)

def test_create_season():
    """测试创建季节值对象"""
    season = Season(
        value=SeasonEnum.SPRING,
        temperature_range=(10, 25),
        humidity_range=(30, 70)
    )
    
    assert season.name == "spring"
    assert season.temperature_range == (10, 25)
    assert season.humidity_range == (30, 70)

def test_invalid_season_temperature():
    """测试无效的季节温度范围"""
    with pytest.raises(ValueError, match="最低温度必须小于最高温度"):
        Season(
            value=SeasonEnum.SPRING,
            temperature_range=(25, 10),  # 最低温度大于最高温度
            humidity_range=(30, 70)
        )

def test_invalid_season_humidity():
    """测试无效的季节湿度范围"""
    with pytest.raises(ValueError, match="湿度必须在0-100%之间"):
        Season(
            value=SeasonEnum.SPRING,
            temperature_range=(10, 25),
            humidity_range=(-10, 110)  # 湿度超出范围
        )

def test_season_suitability():
    """测试季节适应性判断"""
    season = Season(
        value=SeasonEnum.SPRING,
        temperature_range=(10, 25),
        humidity_range=(30, 70)
    )
    
    assert season.is_suitable_temperature(15)
    assert not season.is_suitable_temperature(5)
    assert season.is_suitable_humidity(50)
    assert not season.is_suitable_humidity(80)

def test_create_weather():
    """测试创建天气值对象"""
    weather = Weather(
        value=WeatherEnum.SUNNY,
        temperature=25,
        humidity=60,
        wind_speed=5,
        precipitation=0
    )
    
    assert weather.name == "sunny"
    assert weather.temperature == 25
    assert weather.humidity == 60
    assert weather.wind_speed == 5
    assert weather.precipitation == 0

def test_invalid_weather_temperature():
    """测试无效的天气温度"""
    with pytest.raises(ValueError, match="温度必须在-50到50度之间"):
        Weather(
            value=WeatherEnum.SUNNY,
            temperature=60,  # 温度超出范围
            humidity=60,
            wind_speed=5,
            precipitation=0
        )

def test_invalid_weather_humidity():
    """测试无效的天气湿度"""
    with pytest.raises(ValueError, match="湿度必须在0-100%之间"):
        Weather(
            value=WeatherEnum.SUNNY,
            temperature=25,
            humidity=120,  # 湿度超出范围
            wind_speed=5,
            precipitation=0
        )

def test_weather_outdoor_suitability():
    """测试天气户外适应性判断"""
    good_weather = Weather(
        value=WeatherEnum.SUNNY,
        temperature=25,
        humidity=60,
        wind_speed=5,
        precipitation=0
    )
    
    bad_weather = Weather(
        value=WeatherEnum.RAINY,
        temperature=20,
        humidity=80,
        wind_speed=15,
        precipitation=20
    )
    
    assert good_weather.is_suitable_for_outdoor()
    assert not bad_weather.is_suitable_for_outdoor()

def test_create_occasion():
    """测试创建场合值对象"""
    occasion = Occasion(
        value=OccasionEnum.WORK,
        dress_code="商务休闲",
        formality_level=3,
        suitable_time=["9-18"],
        indoor=True
    )
    
    assert occasion.name == "work"
    assert occasion.dress_code == "商务休闲"
    assert occasion.formality_level == 3
    assert occasion.suitable_time == ["9-18"]
    assert occasion.indoor is True

def test_invalid_occasion_formality():
    """测试无效的场合正式程度"""
    with pytest.raises(ValueError, match="正式程度必须在1-5之间"):
        Occasion(
            value=OccasionEnum.WORK,
            dress_code="商务休闲",
            formality_level=6,  # 正式程度超出范围
            suitable_time=["9-18"],
            indoor=True
        )

def test_occasion_formality():
    """测试场合正式程度判断"""
    formal = Occasion(
        value=OccasionEnum.FORMAL,
        dress_code="正装",
        formality_level=5,
        suitable_time=["9-22"],
        indoor=True
    )
    
    casual = Occasion(
        value=OccasionEnum.DAILY,
        dress_code="休闲",
        formality_level=1,
        suitable_time=["0-24"],
        indoor=False
    )
    
    assert formal.is_formal()
    assert not casual.is_formal()

def test_occasion_time_suitability():
    """测试场合时间适应性判断"""
    work = Occasion(
        value=OccasionEnum.WORK,
        dress_code="商务休闲",
        formality_level=3,
        suitable_time=["9-18"],
        indoor=True
    )
    
    suitable_time = datetime(2024, 3, 18, 14, 0)  # 14:00
    unsuitable_time = datetime(2024, 3, 18, 20, 0)  # 20:00
    
    assert work.is_suitable_time(suitable_time)
    assert not work.is_suitable_time(unsuitable_time) 