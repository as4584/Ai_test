# AI Receptionist - Barebones Deployment Guide

## 🎯 **Purpose**
This is a **latency-optimized barebones version** of the AI receptionist designed for systematic feature testing. We'll measure the latency impact of each feature by starting minimal and progressively adding:

1. ✅ **Baseline** (current) - Minimal Gemini 2.0 Flash integration
2. 🔲 **RAG Context** - Add knowledge base retrieval
3. 🔲 **Enhanced Prompting** - Add detailed system prompts
4. 🔲 **Business Context** - Add hours, services, location
5. 🔲 **Full Stack** - All features combined

---

## 📊 **Current Configuration: BASELINE**

**Included:**
- ✅ FastAPI minimal server
- ✅ Gemini 2.0 Flash API
- ✅ Basic latency logging
- ✅ Metrics endpoint

**NOT Included:**
- ❌ RAG / Knowledge base
- ❌ Database
- ❌ Enhanced prompts
- ❌ Business context
- ❌ Twilio signature validation (optional for testing)
- ❌ Redis queuing

**Expected Latency:** 200-500ms (pure AI + minimal overhead)

---

## 🚀 **Quick Start**

### 1. Build and Deploy

```bash
# Navigate to barebones directory
cd ai_rep

# Build the Docker image
docker-compose build

# Start the service
docker-compose up -d

# Check logs
docker-compose logs -f
```

### 2. Verify Deployment

```bash
# Health check
curl http://localhost:8015/health

# Expected response:
# {
#   "status": "ok",
#   "version": "barebones-latency-test",
#   "service": "ai-receptionist"
# }
```

### 3. Test the API

```bash
# Simple test
curl -X POST http://localhost:8015/test \
  -H "Content-Type: application/json" \
  -d '{"message": "What are your business hours?"}'

# Expected response:
# {
#   "message": "What are your business hours?",
#   "ai_response": "[AI response]",
#   "latency_ms": 456.78,
#   "ai_latency_ms": 450.23,
#   "tokens": {
#     "input": 125,
#     "output": 87
#   },
#   "model": "gemini-2.0-flash-exp"
# }
```

### 4. View Metrics

```bash
# Get aggregated metrics
curl http://localhost:8015/metrics

# Expected response:
# {
#   "total_calls": 10,
#   "ai_latency": {
#     "mean": 456.78,
#     "median": 445.0,
#     "p50": 445.0,
#     "p95": 678.0,
#     "p99": 812.0,
#     "min": 234.0,
#     "max": 1023.0
#   },
#   "total_latency": {...},
#   "overhead": {...},
#   "recent_calls": [...]
# }
```

---

## 📱 **Testing with Phone Calls**

### Configure Twilio Webhook

1. **Get your public URL** (via Caddy reverse proxy):
   ```
   https://lexmakesit.com/ai-receptionist/twilio/webhook
   ```

2. **Update Twilio phone number settings**:
   - Log in to Twilio Console
   - Go to Phone Numbers → Active Numbers
   - Select your number
   - Under "Voice & Fax", set:
     - **A CALL COMES IN**: Webhook
     - **URL**: `https://lexmakesit.com/ai-receptionist/twilio/webhook`
     - **HTTP**: POST

3. **Call the number** and speak or send a message

4. **Check metrics**:
   ```bash
   curl http://localhost:8015/metrics
   ```

---

## 🔧 **Server Deployment**

### Update Caddy Configuration

Edit `/home/lex/lexmakesit-infra/caddy/Caddyfile`:

```caddyfile
# AI Receptionist - Barebones
lexmakesit.com {
    # ... existing config ...
    
    # AI Receptionist barebones (on port 8015)
    handle /ai-receptionist/* {
        reverse_proxy localhost:8015
    }
}
```

Reload Caddy:
```bash
cd /home/lex/lexmakesit-infra
docker-compose exec caddy caddy reload --config /etc/caddy/Caddyfile
```

### Deploy on Server

```bash
# SSH to server (if not already there)
# cd /home/lex/antigravity_bundle/testing/ai_receptionist/ai_rep

# Build and start
docker-compose up -d --build

# Verify
curl http://localhost:8015/health
curl https://lexmakesit.com/ai-receptionist/health
```

---

## 📈 **Latency Testing Workflow**

### Test Sequence

1. **Baseline Test** (current setup)
   ```bash
   # Run 10 test calls
   for i in {1..10}; do
     curl -X POST http://localhost:8015/test \
       -H "Content-Type: application/json" \
       -d '{"message": "What are your hours?"}' -s | jq '.latency_ms'
   done
   
   # Get statistics
   curl http://localhost:8015/metrics | jq '.ai_latency'
   ```

2. **Record Baseline Metrics**
   - Mean latency: _____ ms
   - P95 latency: _____ ms
   - Overhead: _____ ms

3. **Add Feature (e.g., Enhanced Prompting)**
   - Update `ai_service.py` to add detailed prompts
   - Rebuild: `docker-compose up -d --build`
   - Re-run tests
   - Compare metrics

4. **Repeat for Each Feature**
   - Document latency delta for each addition
   - Build latency matrix showing impact

---

## 🧪 **Testing Commands**

### Manual Testing
```bash
# Test with different messages
curl -X POST http://localhost:8015/test \
  -H "Content-Type: application/json" \
  -d '{"message": "I need an appointment"}'

curl -X POST http://localhost:8015/test \
  -H "Content-Type: application/json" \
  -d '{"message": "Tell me about your services"}'
```

### Load Testing
```bash
# Using Apache Bench
ab -n 100 -c 10 -p test_payload.json -T application/json \
  http://localhost:8015/test

# Using wrk (if installed)
wrk -t2 -c10 -d30s --latency \
  -s post.lua http://localhost:8015/test
```

### View Logs in Real-Time
```bash
# Container logs
docker-compose logs -f --tail=50

# Latency metrics file
tail -f data/latency_metrics.jsonl | jq '.'
```

---

## 📊 **Metrics Analysis**

### Extract Metrics from Logs

```bash
# Get average AI latency
jq -s 'map(.ai_latency_ms) | add / length' data/latency_metrics.jsonl

# Get P95 latency
jq -s 'map(.ai_latency_ms) | sort | .[length * 95 / 100 | floor]' \
  data/latency_metrics.jsonl

# Get overhead statistics
jq -s 'map(.overhead_ms) | {
  mean: (add / length),
  min: min,
  max: max
}' data/latency_metrics.jsonl
```

### Compare Before/After Feature Addition

```bash
# Before adding feature
mv data/latency_metrics.jsonl data/baseline_metrics.jsonl

# After adding feature
# ... make changes and test ...

# Compare
echo "Baseline:"
jq -s 'map(.ai_latency_ms) | add / length' data/baseline_metrics.jsonl

echo "With Feature:"
jq -s 'map(.ai_latency_ms) | add / length' data/latency_metrics.jsonl
```

---

## 🔍 **Troubleshooting**

### Service Won't Start

```bash
# Check logs
docker-compose logs

# Common issues:
# 1. GEMINI_API_KEY not set
cat .env | grep GEMINI_API_KEY

# 2. Port 8015 already in use
sudo lsof -i :8015
docker ps | grep 8015

# 3. Permission issues on data directory
ls -la data/
chmod 755 data/
```

### High Latency

```bash
# Check if Gemini API is slow
curl -X POST http://localhost:8015/test \
  -H "Content-Type: application/json" \
  -d '{"message": "test"}' -s | jq '.ai_latency_ms'

# Expected: 200-500ms for Gemini 2.0 Flash
# If > 1000ms, check:
# - Internet connection
# - Gemini API status
# - Server resource usage (CPU, memory)
```

### No Metrics Being Logged

```bash
# Check if data directory is writable
ls -la data/

# Check container has access
docker-compose exec ai-receptionist-barebones ls -la /app/data/

# Manual permission fix
chmod 777 data/
```

---

## 📝 **Next Steps**

### Feature Addition Roadmap

1. **✅ Baseline** - Current state
2. **Enhanced Prompting** - Add detailed system instructions
3. **RAG Integration** - Add knowledge base retrieval
4. **Business Context** - Add operating hours, services
5. **Full Stack** - Combine all features

### Measurement Plan

For each feature:
1. Record baseline metrics (P50, P95, P99)
2. Add feature
3. Re-measure
4. Calculate delta
5. Document findings

### Target Metrics

| Configuration | Target P95 | Max Acceptable |
|---------------|-----------|----------------|
| Baseline      | < 500ms   | < 800ms        |
| + Enhanced    | < 600ms   | < 900ms        |
| + RAG         | < 800ms   | < 1200ms       |
| + Context     | < 650ms   | < 950ms        |
| Full Stack    | < 1000ms  | < 1500ms       |

---

## 🎯 **Success Criteria**

✅ **Deployment Success:**
- Service responds to /health endpoint
- Can process test messages
- Metrics are being logged
- Phone calls connect (if testing with Twilio)

✅ **Baseline Latency:**
- P95 latency < 800ms
- Overhead < 50ms
- No errors in logs

✅ **Ready for Feature Testing:**
- Clean baseline metrics established
- Can rebuild and redeploy easily
- Metrics collection working

---

## 📞 **Support**

If you encounter issues:
1. Check logs: `docker-compose logs -f`
2. Verify .env file has GEMINI_API_KEY
3. Test health endpoint: `curl http://localhost:8015/health`
4. Check metrics: `curl http://localhost:8015/metrics`

---

**Version:** 1.0.0-barebones  
**Last Updated:** 2025-12-01  
**Purpose:** Latency testing and feature impact measurement
