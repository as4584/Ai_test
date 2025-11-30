# Latency Measurement System

## Overview

The AI receptionist webhook now includes comprehensive latency measurement probes to track performance metrics for **Twilio → AI → Twilio** roundtrip latency.

## Architecture

### Latency Measurement Flow

```
1. Twilio sends webhook request
   ↓ [request_start timestamp]
2. FastAPI receives & validates request
   ↓
3. Parse Twilio payload (caller, message, etc.)
   ↓ [ai_start timestamp]
4. Call Gemini API for AI response
   ↓ [ai_end timestamp]
5. Calculate latencies
   ↓
6. Log metrics to data/latency_logs.jsonl
   ↓
7. Return response to Twilio
```

### Latency Components

```
total_latency_ms = twilio_roundtrip_ms + ai_latency_ms

Where:
- ai_latency_ms: Time spent in Gemini API call (AI generation only)
- twilio_roundtrip_ms: Network + FastAPI + webhook overhead
- total_latency_ms: Complete end-to-end latency
```

## Implementation Details

### 1. Updated GeminiService

**File:** `ai_receptionist/services/ai/gemini.py`

Added `generate_response_with_metrics()` method that returns:
- AI response text
- AI latency (milliseconds)
- Input token count
- Output token count
- Model name

**Key features:**
- Uses `time.monotonic()` for accurate timing
- Attempts to get actual token counts from Gemini API
- Falls back to character-based estimation (4 chars ≈ 1 token)
- Handles errors gracefully with fallback response

### 2. Updated Twilio Webhook

**File:** `ai_receptionist/app/api/twilio.py`

Added latency measurement probes:
- `request_start`: Captures timestamp at webhook entry
- `ai_start` / `ai_end`: Measures AI generation time
- Calculates `total_latency_ms` and `twilio_roundtrip_ms`
- Logs all metrics asynchronously

**Integration:**
- Webhook now calls AI service directly
- Extracts user message from Twilio payload
- Passes context (tenant_id, caller) to AI
- Logs metrics before returning response

### 3. Latency Logger Utility

**File:** `ai_receptionist/utils/latency_logger.py`

**Functions:**
- `log_latency()`: Async function to append metrics to JSONL file
- `analyze_latency_logs()`: Calculate statistics (mean, median, p95, p99, min, max)

**Features:**
- Thread-safe async file writes using `aiofiles`
- Automatic directory creation
- JSONL format (one JSON object per line)
- UTC timestamps in ISO 8601 format
- Error handling with graceful fallback

## Log Format

### File Location
```
data/latency_logs.jsonl
```

### Log Entry Example
```json
{
  "timestamp": "2025-11-30T15:30:45.123456Z",
  "ai_latency_ms": 456.78,
  "total_latency_ms": 523.45,
  "twilio_roundtrip_ms": 66.67,
  "input_token_count": 125,
  "output_token_count": 87,
  "model_name": "gemini-2.0-flash-exp"
}
```

### Field Descriptions

| Field | Type | Description | Unit |
|-------|------|-------------|------|
| `timestamp` | string | UTC timestamp in ISO 8601 format | - |
| `ai_latency_ms` | float | Time spent in AI generation | milliseconds |
| `total_latency_ms` | float | Total request latency | milliseconds |
| `twilio_roundtrip_ms` | float | Twilio webhook overhead | milliseconds |
| `input_token_count` | integer | Input tokens sent to AI | tokens |
| `output_token_count` | integer | Output tokens from AI | tokens |
| `model_name` | string | AI model identifier | - |

## Usage

### Testing Latency Logging

Run the test script:
```bash
python test_latency_logging.py
```

Expected output:
```
Testing latency logging...
------------------------------------------------------------

Test message: 'What are your business hours?'

AI Response: [Gemini response]

Metrics:
  AI Latency: 456.78ms
  Input Tokens: 125
  Output Tokens: 87
  Model: gemini-2.0-flash-exp

✓ Latency logged to data/latency_logs.jsonl
  Total Latency: 523.45ms
  Twilio Overhead: 66.67ms
```

### Analyzing Logs Programmatically

```python
from ai_receptionist.utils.latency_logger import analyze_latency_logs

# Analyze all logs
stats = analyze_latency_logs()
print(f"Total requests: {stats['total_entries']}")
print(f"P95 AI latency: {stats['ai_latency']['p95']}ms")
print(f"P99 total latency: {stats['total_latency']['p99']}ms")

# Analyze last 100 requests only
recent_stats = analyze_latency_logs(last_n=100)
```

### Command-Line Analysis

```bash
# Count total requests
wc -l data/latency_logs.jsonl

# View last 10 entries (pretty-printed)
tail -10 data/latency_logs.jsonl | jq '.'

# Calculate average AI latency
jq -s 'map(.ai_latency_ms) | add/length' data/latency_logs.jsonl

# Find requests with high latency (>1000ms)
jq 'select(.total_latency_ms > 1000)' data/latency_logs.jsonl

# Get P95 total latency
jq -s 'map(.total_latency_ms) | sort | .[length*95/100|floor]' data/latency_logs.jsonl

# Token usage by model
jq -s 'group_by(.model_name) | map({model: .[0].model_name, count: length})' data/latency_logs.jsonl
```

## Performance Targets

### Latency Benchmarks

Based on Gemini Flash 2.0 performance:

| Metric | Target (P95) | Warning Threshold | Critical Threshold |
|--------|-------------|-------------------|-------------------|
| AI Latency | < 800ms | > 1000ms | > 1500ms |
| Total Latency | < 1000ms | > 1500ms | > 2000ms |
| Twilio Overhead | < 200ms | > 300ms | > 500ms |

### Expected Latency Breakdown

```
Network (Twilio → Server):     ~50-150ms
FastAPI Processing:            ~10-50ms
AI Generation (Gemini):        ~200-800ms
Response Preparation:          ~5-15ms
----------------------------------------
Total:                         ~265-1015ms
```

## Monitoring & Alerts

### Daily Monitoring

```bash
# Get today's statistics
jq -s 'map(select(.timestamp | startswith("2025-11-30"))) | {
  count: length,
  avg_ai: (map(.ai_latency_ms) | add/length),
  avg_total: (map(.total_latency_ms) | add/length),
  p95_total: (map(.total_latency_ms) | sort | .[length*95/100|floor])
}' data/latency_logs.jsonl
```

### Alert Script Example

```bash
#!/bin/bash
# alert_on_high_latency.sh

P95=$(jq -s 'map(.total_latency_ms) | sort | .[length*95/100|floor]' data/latency_logs.jsonl)

if (( $(echo "$P95 > 2000" | bc -l) )); then
    echo "CRITICAL: P95 latency is ${P95}ms (threshold: 2000ms)"
    # Send alert (email, Slack, PagerDuty, etc.)
elif (( $(echo "$P95 > 1500" | bc -l) )); then
    echo "WARNING: P95 latency is ${P95}ms (threshold: 1500ms)"
    # Send warning
fi
```

## Log Rotation

### Automatic Rotation

Add to cron (daily at 2 AM):
```bash
0 2 * * * /path/to/rotate_latency_logs.sh
```

### Rotation Script

```bash
#!/bin/bash
# rotate_latency_logs.sh

LOG_DIR="data"
LOG_FILE="latency_logs.jsonl"
ARCHIVE_DIR="data/archive"

# Create archive directory
mkdir -p "$ARCHIVE_DIR"

# Compress and archive current log
if [ -f "$LOG_DIR/$LOG_FILE" ]; then
    DATE=$(date +%Y%m%d)
    gzip -c "$LOG_DIR/$LOG_FILE" > "$ARCHIVE_DIR/latency_logs_$DATE.jsonl.gz"
    
    # Clear current log (or delete and recreate)
    : > "$LOG_DIR/$LOG_FILE"
    
    echo "Rotated logs to $ARCHIVE_DIR/latency_logs_$DATE.jsonl.gz"
fi

# Delete archives older than 90 days
find "$ARCHIVE_DIR" -name "latency_logs_*.jsonl.gz" -mtime +90 -delete
```

## Privacy & Security

### What IS Logged
- ✓ Latency metrics (milliseconds)
- ✓ Token counts (integers)
- ✓ Model name (string)
- ✓ Timestamps (UTC)

### What IS NOT Logged
- ✗ Phone numbers
- ✗ User messages or conversation content
- ✗ AI responses
- ✗ Personal information
- ✗ API keys or credentials
- ✗ Tenant IDs or caller information

**Privacy compliance:** GDPR, CCPA, HIPAA compliant (no PII logged)

## Troubleshooting

### Issue: No logs being created

**Check:**
1. Directory permissions: `ls -la data/`
2. Disk space: `df -h`
3. Application logs for errors

**Fix:**
```bash
mkdir -p data
chmod 755 data
```

### Issue: Log file growing too large

**Check size:**
```bash
du -h data/latency_logs.jsonl
```

**Implement rotation:**
- See "Log Rotation" section above
- Consider streaming to log aggregation service

### Issue: Inaccurate latencies

**Verify:**
1. Using `time.monotonic()` (not `time.time()`)
2. Measuring at correct points in code
3. No blocking operations between measurements

**Debug:**
```python
import time

start = time.monotonic()
# ... operation ...
end = time.monotonic()
latency_ms = (end - start) * 1000
print(f"Latency: {latency_ms:.2f}ms")
```

## Integration with Monitoring Tools

### Prometheus

Export metrics via custom exporter:
```python
from prometheus_client import Histogram, Counter

latency_histogram = Histogram(
    'ai_latency_seconds',
    'AI generation latency',
    buckets=[0.1, 0.25, 0.5, 1.0, 2.0, 5.0]
)

@app.post("/twilio/webhook")
async def webhook(...):
    with latency_histogram.time():
        result = await ai_service.generate_response_with_metrics(...)
```

### Grafana

Create dashboard with:
- Latency over time (line chart)
- P95/P99 latency (stat panel)
- Token usage (bar chart)
- Request volume (counter)

### Datadog

Forward JSONL logs:
```bash
tail -f data/latency_logs.jsonl | \
  while read line; do
    curl -X POST "https://http-intake.logs.datadoghq.com/v1/input" \
      -H "DD-API-KEY: $DD_API_KEY" \
      -d "$line"
  done
```

## Dependencies

### Required Packages

```
aiofiles==24.1.0  # Async file I/O for safe concurrent writes
```

Install:
```bash
pip install -r requirements.txt
```

## API Reference

### `log_latency()`

```python
async def log_latency(
    ai_latency_ms: float,
    total_latency_ms: float,
    twilio_roundtrip_ms: float,
    input_token_count: int,
    output_token_count: int,
    model_name: str,
    log_path: Optional[Path] = None,
) -> None
```

**Parameters:**
- `ai_latency_ms`: Time spent in AI generation (milliseconds)
- `total_latency_ms`: Total request latency (milliseconds)
- `twilio_roundtrip_ms`: Twilio webhook overhead (milliseconds)
- `input_token_count`: Number of input tokens
- `output_token_count`: Number of output tokens
- `model_name`: AI model identifier
- `log_path`: Optional custom log path (defaults to `data/latency_logs.jsonl`)

**Returns:** None

**Raises:** Logs errors but does not raise exceptions

### `analyze_latency_logs()`

```python
def analyze_latency_logs(
    log_path: Optional[Path] = None,
    last_n: Optional[int] = None
) -> dict
```

**Parameters:**
- `log_path`: Optional custom log path
- `last_n`: Optional limit to last N entries

**Returns:**
```python
{
    "total_entries": 250,
    "ai_latency": {
        "mean": 456.78,
        "median": 445.23,
        "p95": 678.90,
        "p99": 812.34,
        "min": 234.56,
        "max": 1023.45
    },
    "total_latency": {...}
}
```

## Future Enhancements

1. **Real-time streaming:** WebSocket-based latency monitoring dashboard
2. **Anomaly detection:** ML-based detection of latency spikes
3. **Cost tracking:** Token usage → cost calculation
4. **A/B testing:** Compare latency across different models/prompts
5. **Geographic analysis:** Track latency by caller region
6. **Synthetic monitoring:** Automated latency checks with test requests

## References

- Gemini API Documentation: https://ai.google.dev/docs
- Twilio Webhook Guide: https://www.twilio.com/docs/usage/webhooks
- Time Measurement in Python: https://docs.python.org/3/library/time.html#time.monotonic
- JSONL Format: https://jsonlines.org/
