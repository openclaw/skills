# seoul-subway

Seoul Metro information skill for Claude.

## Features

- **Real-time Arrival** - Train arrival times by station
- **Station Search** - Line and station code lookup
- **Route Search** - Shortest path, travel time, fare
- **Service Alerts** - Delays, incidents, express stops

## Environment Variables

| Variable | Provider | Required Data |
|----------|----------|---------------|
| `SEOUL_OPENAPI_KEY` | [data.seoul.go.kr](https://data.seoul.go.kr) | 실시간 지하철 인증키 |
| `DATA_GO_KR_KEY` | [data.go.kr](https://data.go.kr) | 서울교통공사_지하철알림정보, 서울교통공사_최단경로이동정보 |

## Usage

```
"강남역 도착정보"
"강남역 몇호선?"
"신도림에서 서울역"
"지하철 지연 있어?"
```

## License

MIT
