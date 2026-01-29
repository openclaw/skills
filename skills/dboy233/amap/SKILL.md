---
name: amap
description: 使用高德地图Web服务API进行地点搜索、天气查询和路线规划。
homepage: https://lbs.amap.com/
metadata: {"clawdbot":{"emoji":"🗺️","requires":{"bins":["curl"]},"primaryEnv":"AMAP_KEY"}}
---

# 高德地图 (Amap)

本技能使用高德地图 Web 服务 API 提供丰富的地理位置服务。

**重要：** 使用本技能前，你必须在高德开放平台申请一个 Web 服务 API Key，并将其设置为环境变量 `AMAP_KEY`。

```bash
export AMAP_KEY="你的Web服务API Key"
```

Clawdbot 会自动读取这个环境变量来调用 API。

## 何时使用 (触发条件)

当用户提出以下类型的请求时，应优先使用本技能：
- "帮我查一下[城市]的天气"
- "搜索[地点]附近的[东西]"
- "查找[关键词]的位置"
- "从[A]到[B]怎么走？"
- "查询[地址]的经纬度"
- "这个坐标[经度,纬度]是哪里？"

## 核心功能与用法

### 1. 天气查询

用于查询指定城市的实时天气或天气预报。

**注意：** API 需要城市的 `adcode`。如果不知道 adcode，可以先通过 **行政区划查询** 功能获取。

#### 查询实时天气
```bash
# 将 [城市adcode] 替换为实际的行政区编码, 例如北京是 110000
curl "https://restapi.amap.com/v3/weather/weatherInfo?key=$AMAP_KEY&city=[城市adcode]&extensions=base"
```

#### 查询天气预报
```bash
# 将 [城市adcode] 替换为实际的行政区编码
curl "https://restapi.amap.com/v3/weather/weatherInfo?key=$AMAP_KEY&city=[城市adcode]&extensions=all"
```

### 2. 地点搜索 (POI)

用于根据关键字在指定城市搜索地点信息。

```bash
# 将 [关键词] 和 [城市] 替换为用户提供的内容
curl "https://restapi.amap.com/v3/place/text?key=$AMAP_KEY&keywords=[关键词]&city=[城市]"
```

### 3. 驾车路径规划

用于规划两个地点之间的驾车路线。

**注意：** API 需要起终点的经纬度坐标。如果用户提供的是地址，需要先通过 **地理编码** 功能将地址转换为坐标。

```bash
# 将 [起点经纬度] 和 [终点经纬度] 替换为实际坐标，格式为 "经度,纬度"
curl "https://restapi.amap.com/v3/direction/driving?key=$AMAP_KEY&origin=[起点经纬度]&destination=[终点经纬度]"
```

### 4. 地理编码 (地址 → 坐标)

将结构化的地址信息转换为经纬度坐标。

```bash
# 将 [地址] 替换为用户提供的地址
curl "https://restapi.amap.com/v3/geocode/geo?key=$AMAP_KEY&address=[地址]"
```

### 5. 逆地理编码 (坐标 → 地址)

将经纬度坐标转换为结构化的地址信息。

```bash
# 将 [经纬度] 替换为实际坐标，格式为 "经度,纬度"
curl "https://restapi.amap.com/v3/geocode/regeo?key=$AMAP_KEY&location=[经纬度]"
```

### 6. 行政区划查询 (获取 adcode)

用于查询省、市、区、街道的行政区划信息，包括 `adcode` 和边界。

```bash
# 将 [关键词] 替换为城市或区域名称，例如 "北京市"
curl "https://restapi.amap.com/v3/config/district?key=$AMAP_KEY&keywords=[关键词]&subdistrict=0"
```
