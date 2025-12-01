# AI Receptionist - Barebones Latency Testing

> **Minimal implementation for systematic latency measurement and feature impact testing**

## 🎯 Quick Start

```bash
# Build and start
docker-compose up -d --build

# Check health
curl http://localhost:8015/health

# Run a test
curl -X POST http://localhost:8015/test \
  -H "Content-Type: application/json" \
  -d '{"message": "What are your hours?"}'

# View metrics
curl http://localhost:8015/metrics
```

## 📊 What's Included

**Baseline Configuration:**
- ✅ Gemini 2.0 Flash (ultra-low latency)
- ✅ Minimal FastAPI server
- ✅ Latency measurement & logging
- ✅ Metrics endpoint

**What's NOT included (for now):**
- ❌ RAG / Knowledge base
- ❌ Database
- ❌ Enhanced prompts
- ❌ Business context

## 🧪 Testing

See [DEPLOYMENT.md](./DEPLOYMENT.md) for complete testing guide.

**Quick test:**
```bash
# 10 test calls
for i in {1..10}; do
  curl -s -X POST http://localhost:8015/test \
    -H "Content-Type: application/json" \
    -d '{"message": "test"}' | jq '.latency_ms'
done

# Get statistics
curl http://localhost:8015/metrics | jq '.ai_latency'
```

## 📈 Expected Latency

| Metric | Target | Max |
|--------|--------|-----|
| AI Latency (P95) | < 500ms | < 800ms |
| Total Latency (P95) | < 600ms | < 900ms |
| Overhead | < 50ms | < 100ms |

## 📝 Next Steps

1. **Establish Baseline** - Run tests, document metrics
2. **Add Feature** - Enhanced prompts, RAG, etc.
3. **Re-measure** - Compare latency delta
4. **Document** - Build feature impact matrix

## 🔧 Troubleshooting

```bash
# Check logs
docker-compose logs -f

# Rebuild
docker-compose down
docker-compose up -d --build

# Check environment
cat .env | grep GEMINI_API_KEY
```

## 📞 Endpoints

- `GET /` - API info
- `GET /health` - Health check
- `POST /twilio/webhook` - Twilio webhook (for phone calls)
- `POST /test` - Manual testing endpoint
- `GET /metrics` - Latency statistics

---

**Version:** 1.0.0-barebones  
**Purpose:** Latency testing baseline  
**Model:** Gemini 2.0 Flash Experimental
