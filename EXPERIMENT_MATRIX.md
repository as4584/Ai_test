# Experiment Matrix

Automated latency experiments across different AI receptionist configurations.

## Overview

The experiment matrix runs controlled tests across four configurations to measure the impact of different features on:
- **Latency** (AI response time)
- **Token usage** (input + output tokens)
- **Estimated cost** (based on Gemini pricing)

## Configurations

### 1. Baseline
- **Description:** Minimal prompt, no RAG
- **Features:**
  - ✗ RAG enabled
  - ✗ Enhanced prompting
  - ✗ Business context
- **Use case:** Fastest, lowest cost, minimal context

### 2. RAG Enabled
- **Description:** With RAG context injection
- **Features:**
  - ✓ RAG enabled (knowledge base retrieval)
  - ✗ Enhanced prompting
  - ✗ Business context
- **Use case:** Access to knowledge base without prompt overhead

### 3. Enhanced Prompting
- **Description:** Detailed system prompts + business context
- **Features:**
  - ✗ RAG enabled
  - ✓ Enhanced prompting (detailed instructions)
  - ✓ Business context (hours, services, location)
- **Use case:** Better quality responses without external retrieval

### 4. Full Stack
- **Description:** RAG + enhanced prompts + business context
- **Features:**
  - ✓ RAG enabled
  - ✓ Enhanced prompting
  - ✓ Business context
- **Use case:** Maximum quality, highest latency/cost

## Running Experiments

### Prerequisites

```bash
# Install dependencies
pip install -r requirements.txt

# Configure Gemini API key
echo "GEMINI_API_KEY=your_key_here" >> .env
```

### Execute

```bash
python experiment_matrix.py
```

### Expected Runtime
- **Total calls:** 20 (4 configurations × 5 calls each)
- **Estimated duration:** 30-90 seconds
- **Estimated cost:** ~$0.001-0.003 USD

## Output

### Console Output

```
╔══════════════════════════════════════════════════════════════════════════════╗
║                        LATENCY EXPERIMENT MATRIX                             ║
╚══════════════════════════════════════════════════════════════════════════════╝

Model: gemini-2.0-flash-exp
Configurations: 4
Calls per config: 5
Total calls: 20

================================================================================
Running: Baseline
Description: Minimal prompt, no RAG
================================================================================

  [1/5] Testing: 'What are your business hours?'
      ✓ Latency: 456.78ms | Tokens: 125 | Cost: $0.000045

  [2/5] Testing: 'I need to schedule an appointment for next Tue...'
      ✓ Latency: 523.12ms | Tokens: 148 | Cost: $0.000052

...

================================================================================
EXPERIMENT MATRIX RESULTS - COMPARISON TABLE
================================================================================

Configuration             Avg Latency     Tokens/Call     Cost/Call       Total Cost      Success   
------------------------------------------------------------------------------------------------------------------------
Baseline                  456.78ms        125             $0.000045       $0.000225       5/5       
Rag Enabled               512.34ms        178             $0.000062       $0.000310       5/5       
Enhanced Prompting        489.23ms        156             $0.000055       $0.000275       5/5       
Full Stack                567.89ms        203             $0.000071       $0.000355       5/5       

DETAILED STATISTICS
------------------------------------------------------------------------------------------------------------------------

Baseline:
  Latency: avg=456.78ms, min=412.34ms, max=523.45ms
  Tokens: avg=125/call, total=625
  Cost: avg=$0.000045/call, total=$0.000225

Rag Enabled:
  Latency: avg=512.34ms, min=467.12ms, max=589.23ms
  Tokens: avg=178/call, total=890
  Cost: avg=$0.000062/call, total=$0.000310

...
```

### JSON Output

Results saved to `data/latency_matrix.json`:

```json
{
  "experiment_metadata": {
    "timestamp": "2025-11-30T16:45:23.123456Z",
    "total_configurations": 4,
    "calls_per_config": 5,
    "model": "gemini-2.0-flash-exp",
    "pricing": {
      "input_cost_per_1M_tokens": 0.075,
      "output_cost_per_1M_tokens": 0.30
    }
  },
  "configurations": { ... },
  "test_messages": [ ... ],
  "results": [
    {
      "config": { ... },
      "aggregate": {
        "config_name": "baseline",
        "config_description": "Minimal prompt, no RAG",
        "total_calls": 5,
        "successful_calls": 5,
        "failed_calls": 0,
        "avg_ai_latency_ms": 456.78,
        "max_ai_latency_ms": 523.45,
        "min_ai_latency_ms": 412.34,
        "avg_total_tokens": 125,
        "total_tokens_all_calls": 625,
        "total_cost_usd": 0.000225,
        "avg_cost_per_call_usd": 0.000045
      },
      "individual_results": [ ... ]
    }
  ]
}
```

## Analysis

### Query Results with jq

```bash
# View all aggregate stats
cat data/latency_matrix.json | jq '.results[].aggregate'

# Compare configurations
cat data/latency_matrix.json | jq '.results[] | {
  config: .aggregate.config_name,
  latency: .aggregate.avg_ai_latency_ms,
  tokens: .aggregate.avg_total_tokens,
  cost: .aggregate.total_cost_usd
}'

# Find fastest configuration
cat data/latency_matrix.json | jq '.results | 
  sort_by(.aggregate.avg_ai_latency_ms) | 
  .[0].aggregate.config_name'

# Find most cost-effective
cat data/latency_matrix.json | jq '.results | 
  sort_by(.aggregate.avg_cost_per_call_usd) | 
  .[0].aggregate.config_name'

# Calculate total experiment cost
cat data/latency_matrix.json | jq '[.results[].aggregate.total_cost_usd] | add'

# Get individual call details for specific config
cat data/latency_matrix.json | jq '.results[] | 
  select(.aggregate.config_name == "baseline") | 
  .individual_results[]'
```

### Python Analysis

```python
import json

# Load results
with open('data/latency_matrix.json') as f:
    data = json.load(f)

# Extract aggregates
aggregates = [r['aggregate'] for r in data['results']]

# Find config with best latency/cost ratio
best_ratio = min(
    aggregates,
    key=lambda a: a['avg_ai_latency_ms'] / (a['avg_cost_per_call_usd'] * 1000000)
)
print(f"Best latency/cost ratio: {best_ratio['config_name']}")

# Compare latency overhead
baseline = next(a for a in aggregates if a['config_name'] == 'baseline')
full_stack = next(a for a in aggregates if a['config_name'] == 'full_stack')

latency_overhead = full_stack['avg_ai_latency_ms'] - baseline['avg_ai_latency_ms']
cost_overhead = full_stack['total_cost_usd'] - baseline['total_cost_usd']

print(f"Full stack overhead: +{latency_overhead:.2f}ms, +${cost_overhead:.6f}")
```

## Expected Results

### Typical Latency Ranges

| Configuration | Avg Latency | Token Overhead | Cost Overhead |
|---------------|-------------|----------------|---------------|
| Baseline | 400-500ms | 0% (reference) | 0% (reference) |
| RAG Enabled | 480-580ms | +30-50% | +30-50% |
| Enhanced Prompting | 450-550ms | +20-30% | +20-30% |
| Full Stack | 550-650ms | +50-80% | +50-80% |

### Trade-offs

**Baseline:**
- ✓ Fastest response time
- ✓ Lowest cost
- ✗ Limited context
- ✗ Generic responses

**RAG Enabled:**
- ✓ Access to knowledge base
- ✓ Accurate information
- ✗ Retrieval overhead
- ✗ Higher token usage

**Enhanced Prompting:**
- ✓ Better response quality
- ✓ Professional tone
- ✗ Increased prompt size
- ≈ Moderate latency increase

**Full Stack:**
- ✓ Highest quality responses
- ✓ Maximum context
- ✗ Highest latency
- ✗ Highest cost

## Customization

### Modify Test Messages

Edit `TEST_MESSAGES` in `experiment_matrix.py`:

```python
TEST_MESSAGES = [
    "Your custom message 1",
    "Your custom message 2",
    # Add more messages...
]
```

### Add New Configurations

Add to `CONFIGURATIONS` dict:

```python
CONFIGURATIONS = {
    # ... existing configs ...
    "custom_config": {
        "name": "Custom Config",
        "description": "Your custom configuration",
        "rag_enabled": True,
        "enhanced_prompting": False,
        "business_context": True,
    }
}
```

### Adjust Test Volume

Modify the number of test messages or repeat the same messages:

```python
# Run 10 calls per config instead of 5
TEST_MESSAGES = [
    "Message 1",
    "Message 2",
    "Message 3",
    "Message 4",
    "Message 5",
] * 2  # Repeat each message twice
```

## Integration with Production

### A/B Testing

Use experiment results to configure production routing:

```python
# Based on experiment results, route calls by priority
if customer_tier == "premium":
    config = "full_stack"  # Best quality
elif query_type == "complex":
    config = "rag_enabled"  # Knowledge base access
elif time_sensitive:
    config = "baseline"  # Fastest response
else:
    config = "enhanced_prompting"  # Balanced
```

### Cost Optimization

Calculate monthly costs based on call volume:

```python
# From experiment results
cost_per_call = {
    "baseline": 0.000045,
    "rag_enabled": 0.000062,
    "enhanced_prompting": 0.000055,
    "full_stack": 0.000071,
}

# Monthly projections
monthly_calls = 10000
config = "full_stack"

monthly_cost = monthly_calls * cost_per_call[config]
print(f"Estimated monthly cost: ${monthly_cost:.2f}")
```

### Latency Budgets

Set SLAs based on measured latencies:

```python
# P95 latency from experiments + 20% buffer
latency_sla = {
    "baseline": 600,      # 500ms P95 + 20%
    "rag_enabled": 700,   # 580ms P95 + 20%
    "enhanced_prompting": 660,  # 550ms P95 + 20%
    "full_stack": 780,    # 650ms P95 + 20%
}

# Alert if production exceeds SLA
if actual_latency > latency_sla[config]:
    send_alert(f"Latency SLA breach: {actual_latency}ms > {latency_sla[config]}ms")
```

## Continuous Experimentation

### Scheduled Runs

Run experiments weekly to track performance trends:

```bash
# Add to crontab (every Monday at 2 AM)
0 2 * * 1 cd /path/to/ai_receptionist && python experiment_matrix.py >> logs/experiments.log 2>&1
```

### Version Tracking

Track experiments alongside code changes:

```bash
# Tag experiment results with git commit
git log -1 --pretty=format:"%H" > data/experiment_git_sha.txt
python experiment_matrix.py

# Commit results for tracking
git add data/latency_matrix.json data/experiment_git_sha.txt
git commit -m "perf: Experiment results for commit $(cat data/experiment_git_sha.txt)"
```

### Regression Detection

Compare with previous results:

```python
import json

# Load current and previous results
with open('data/latency_matrix.json') as f:
    current = json.load(f)

with open('data/latency_matrix_previous.json') as f:
    previous = json.load(f)

# Compare each configuration
for curr_result in current['results']:
    config_name = curr_result['aggregate']['config_name']
    prev_result = next(
        r for r in previous['results'] 
        if r['aggregate']['config_name'] == config_name
    )
    
    curr_latency = curr_result['aggregate']['avg_ai_latency_ms']
    prev_latency = prev_result['aggregate']['avg_ai_latency_ms']
    
    diff = curr_latency - prev_latency
    pct_change = (diff / prev_latency) * 100
    
    if abs(pct_change) > 10:  # Alert on >10% change
        print(f"⚠️ {config_name}: {pct_change:+.1f}% latency change")
```

## Troubleshooting

### Issue: Rate Limiting

**Symptom:** Errors after several calls

**Solution:** Increase delay between configs:
```python
# In experiment_matrix.py
await asyncio.sleep(2)  # Increase from 1 to 2 seconds
```

### Issue: Inconsistent Results

**Symptom:** High variance in latencies

**Solution:** Run more trials per config:
```python
# Repeat each message 3 times
TEST_MESSAGES = [
    "Message 1", "Message 1", "Message 1",
    "Message 2", "Message 2", "Message 2",
    # ...
]
```

### Issue: API Key Errors

**Symptom:** "GEMINI_API_KEY not configured" error

**Solution:**
```bash
# Check .env file exists
ls -la .env

# Add API key
echo "GEMINI_API_KEY=your_actual_key_here" >> .env

# Verify it's loaded
python -c "from ai_receptionist.config.settings import get_settings; print(get_settings().gemini_api_key[:10])"
```

## References

- Gemini API Pricing: https://ai.google.dev/pricing
- Gemini API Documentation: https://ai.google.dev/docs
- Token Estimation: https://ai.google.dev/models/gemini#token-limits
