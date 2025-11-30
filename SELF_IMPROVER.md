# Self-Improvement System

Automated performance monitoring and regression detection for the AI Receptionist.

## Overview

`self_improver.py` watches critical code files for changes, automatically runs experiments, detects performance regressions, and provides optimization recommendations.

## Features

✅ **Automatic File Watching**
- Monitors `ai_receptionist/services/ai/gemini.py`
- Monitors `ai_receptionist/app/api/twilio.py`
- Debounced change detection (2-second cooldown)

✅ **Automated Experiment Execution**
- Runs `experiment_matrix.py` on file changes
- Captures results and metrics
- Timeout protection (3 minutes)

✅ **Regression Detection**
- Compares current vs. previous results
- Flags latency increases > 20%
- Tracks all 4 configurations (baseline, RAG, enhanced, full_stack)

✅ **Performance Analysis**
- Identifies improvements and regressions
- Calculates percent changes
- Tracks cost impact

✅ **Optimization Recommendations**
- Configuration-specific suggestions
- Cost optimization advice
- Caching and async recommendations

✅ **Experiment History**
- JSONL log of all experiments (`data/experiment_history.jsonl`)
- Tracks trigger source (file change, manual, etc.)
- Historical trend analysis

## Installation

```bash
# Install watchdog dependency
pip install watchdog==4.0.0

# Or install from requirements.txt
pip install -r requirements.txt
```

## Usage

### Start Monitoring

```bash
python self_improver.py
```

**What happens:**
1. Runs initial baseline experiment
2. Starts watching files for changes
3. Automatically re-runs experiments on code modifications
4. Prints regression analysis after each run

### Expected Output

```
👁️  Self-Improvement System Started
================================================================================
Watching files:
  ✓ ai_receptionist/services/ai/gemini.py
  ✓ ai_receptionist/app/api/twilio.py

Regression threshold: 20.0%
Results: data/latency_matrix.json
History: data/experiment_history.jsonl

Press Ctrl+C to stop
================================================================================

🚀 Running initial baseline experiment...
🔬 Running experiments (trigger: initial_baseline)...
⏱️  This will take 30-90 seconds...
✅ Experiments completed

📊 Analyzing results...
📈 Current Metrics:
────────────────────────────────────────────────────────────────────────────────
baseline                     456.7ms    625 tokens  $0.000225
rag_enabled                  512.3ms    890 tokens  $0.000310
extra_prompting_enabled      489.2ms    780 tokens  $0.000275
full_stack                   567.9ms   1015 tokens  $0.000355

📌 Baseline established (no previous results to compare)
────────────────────────────────────────────────────────────────────────────────

👀 Monitoring for changes...
```

### When File Changes

```
📝 Detected change in: gemini.py

🔬 Running experiments (trigger: file_change: gemini.py)...
⏱️  This will take 30-90 seconds...
✅ Experiments completed

📊 Analyzing results...
📈 Current Metrics:
────────────────────────────────────────────────────────────────────────────────
baseline                     478.2ms    625 tokens  $0.000225
rag_enabled                  698.7ms    890 tokens  $0.000310
extra_prompting_enabled      501.4ms    780 tokens  $0.000275
full_stack                   589.3ms   1015 tokens  $0.000355

🔍 Regression Analysis:
────────────────────────────────────────────────────────────────────────────────
⚠️  PERFORMANCE REGRESSIONS DETECTED:

⚠️  rag_enabled: +186.4ms (36.4% increase)
   → Check RAG context size and retrieval efficiency
   → Cost increased by $0.000000 (+0.0%)

🎯 Regression threshold: 20.0%
────────────────────────────────────────────────────────────────────────────────
```

### With Improvements

```
🔍 Regression Analysis:
────────────────────────────────────────────────────────────────────────────────
✅ No significant regressions detected

💚 Performance Improvements:
   ✓ baseline: -12.3ms (2.7% faster)
   ✓ full_stack: -23.1ms (4.1% faster)
```

## Regression Detection

### Threshold

Default: **20% latency increase**

A configuration triggers a warning if:
```
(current_latency - baseline_latency) / baseline_latency > 0.20
```

### Recommendations

The system provides context-specific advice:

**RAG-enabled configurations:**
```
→ Check RAG context size and retrieval efficiency
```

**Enhanced prompting configurations:**
```
→ Review prompt complexity and token count
```

**Large latency increases (>200ms):**
```
→ Consider caching or async optimizations
```

**Cost increases:**
```
→ Cost increased by $0.000123 (+45.6%)
```

## Files Generated

### `data/experiment_history.jsonl`

JSONL log of all experiments:

```json
{"timestamp": "2025-11-30T15:30:45.123456", "trigger": "initial_baseline", "model": "gemini-2.0-flash-exp", "aggregates": {"baseline": {"avg_ai_latency_ms": 456.7, ...}, ...}}
{"timestamp": "2025-11-30T15:35:12.789012", "trigger": "file_change: gemini.py", "model": "gemini-2.0-flash-exp", "aggregates": {...}}
```

**Fields:**
- `timestamp`: ISO 8601 timestamp
- `trigger`: What triggered the experiment (file_change, manual, etc.)
- `model`: AI model used
- `aggregates`: Full metrics for all configurations

### `data/latency_matrix.json`

Latest experiment results (updated on each run)

See `EXPERIMENT_MATRIX.md` for format details.

## Analysis Examples

### View Experiment History

```bash
# Show all experiment timestamps and triggers
cat data/experiment_history.jsonl | jq -r '[.timestamp, .trigger] | @tsv'

# Get baseline latency over time
cat data/experiment_history.jsonl | jq -r '[.timestamp, .aggregates.baseline.avg_ai_latency_ms] | @tsv'

# Find worst regression
cat data/experiment_history.jsonl | jq -s '
  [.[] | .aggregates.baseline.avg_ai_latency_ms] |
  max
'
```

### Python Analysis

```python
import json

# Load history
with open('data/experiment_history.jsonl') as f:
    history = [json.loads(line) for line in f]

# Plot baseline latency over time
import matplotlib.pyplot as plt

timestamps = [entry['timestamp'] for entry in history]
latencies = [entry['aggregates']['baseline']['avg_ai_latency_ms'] for entry in history]

plt.plot(timestamps, latencies)
plt.xlabel('Time')
plt.ylabel('Latency (ms)')
plt.title('Baseline Latency Over Time')
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig('latency_trend.png')
```

## Configuration

### Change Regression Threshold

Edit `self_improver.py`:

```python
REGRESSION_THRESHOLD = 0.15  # 15% instead of 20%
```

### Watch Additional Files

Edit `WATCHED_FILES`:

```python
WATCHED_FILES = [
    "ai_receptionist/services/ai/gemini.py",
    "ai_receptionist/app/api/twilio.py",
    "ai_receptionist/config/settings.py",  # Add more files
]
```

### Change Debounce Time

Prevent multiple triggers on rapid file saves:

```python
self.debounce_seconds = 5  # Wait 5 seconds instead of 2
```

## Workflow Examples

### 1. Continuous Development

```bash
# Terminal 1: Start monitoring
python self_improver.py

# Terminal 2: Make code changes
vim ai_receptionist/services/ai/gemini.py

# Automatically runs experiments on save
# Shows regression analysis immediately
```

### 2. Pre-Commit Hook

```bash
#!/bin/bash
# .git/hooks/pre-commit

# Run single experiment and check for regressions
python experiment_matrix.py

# Parse latest results
REGRESSION=$(python -c "
import json
with open('data/experiment_history.jsonl') as f:
    lines = f.readlines()
    if len(lines) >= 2:
        prev = json.loads(lines[-2])
        curr = json.loads(lines[-1])
        
        for config in curr['aggregates']:
            prev_lat = prev['aggregates'][config]['avg_ai_latency_ms']
            curr_lat = curr['aggregates'][config]['avg_ai_latency_ms']
            
            if (curr_lat - prev_lat) / prev_lat > 0.20:
                print('REGRESSION')
                exit(1)
")

if [ "$REGRESSION" = "REGRESSION" ]; then
    echo "❌ Performance regression detected. Commit blocked."
    exit 1
fi
```

### 3. Daily Performance Report

```bash
#!/bin/bash
# cron: 0 9 * * * /path/to/daily_report.sh

cd /path/to/ai_receptionist

# Run experiment
python experiment_matrix.py

# Generate report
echo "Daily Performance Report - $(date)" > report.txt
echo "=================================" >> report.txt
echo "" >> report.txt

cat data/experiment_history.jsonl | tail -7 | jq -r '
  [
    .timestamp,
    .aggregates.baseline.avg_ai_latency_ms,
    .aggregates.full_stack.avg_ai_latency_ms
  ] | @tsv
' >> report.txt

# Email report
mail -s "AI Receptionist Performance" admin@example.com < report.txt
```

## Troubleshooting

### "watchdog not installed"

```bash
pip install watchdog==4.0.0
```

### No changes detected

Check file paths are correct:
```bash
ls -la ai_receptionist/services/ai/gemini.py
ls -la ai_receptionist/app/api/twilio.py
```

### Experiments timing out

Increase timeout in `self_improver.py`:
```python
result = subprocess.run(
    [sys.executable, EXPERIMENT_SCRIPT],
    timeout=300,  # 5 minutes instead of 3
)
```

### Too many false positives

Increase regression threshold:
```python
REGRESSION_THRESHOLD = 0.30  # 30% threshold
```

### History file too large

Rotate the history file:
```bash
# Keep last 100 entries
tail -100 data/experiment_history.jsonl > data/experiment_history.jsonl.tmp
mv data/experiment_history.jsonl.tmp data/experiment_history.jsonl
```

## Integration with CI/CD

### GitHub Actions

```yaml
name: Performance Regression Check

on: [pull_request]

jobs:
  regression-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Install dependencies
        run: pip install -r requirements.txt
      
      - name: Run experiment
        env:
          GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}
        run: python experiment_matrix.py
      
      - name: Check for regressions
        run: |
          python -c "
          import json, sys
          with open('data/latency_matrix.json') as f:
              data = json.load(f)
          
          # Compare with main branch baseline (stored in S3/artifact)
          # ... regression logic ...
          "
      
      - name: Upload results
        uses: actions/upload-artifact@v2
        with:
          name: experiment-results
          path: data/latency_matrix.json
```

## Advanced Features

### Custom Metrics

Track additional metrics by modifying the comparison logic:

```python
# In RegressionDetector.compare()
token_increase = (
    current[config_name]['total_tokens'] - 
    baseline[config_name]['total_tokens']
) / baseline[config_name]['total_tokens']

if token_increase > 0.30:  # 30% more tokens
    regressions.append({
        'type': 'token_regression',
        'config': config_name,
        'percent_increase': token_increase * 100,
    })
```

### Alerts

Send alerts on regressions:

```python
# In SelfImprover.analyze_results()
if has_regression:
    import smtplib
    from email.message import EmailMessage
    
    msg = EmailMessage()
    msg['Subject'] = 'Performance Regression Detected'
    msg['From'] = 'alerts@example.com'
    msg['To'] = 'team@example.com'
    msg.set_content(f"Regressions detected:\n\n{recommendations}")
    
    with smtplib.SMTP('localhost') as s:
        s.send_message(msg)
```

### Slack Notifications

```python
import requests

def send_slack_alert(regressions):
    webhook_url = os.getenv('SLACK_WEBHOOK_URL')
    
    message = {
        'text': '⚠️ Performance Regression Detected',
        'blocks': [
            {
                'type': 'section',
                'text': {
                    'type': 'mrkdwn',
                    'text': '\n'.join([
                        f"• {r['config']}: +{r['percent_increase']:.1f}%"
                        for r in regressions
                    ])
                }
            }
        ]
    }
    
    requests.post(webhook_url, json=message)
```

## Performance Tips

1. **Debounce file changes** to avoid excessive experiments during rapid edits
2. **Run experiments async** to avoid blocking the watcher
3. **Sample history** to prevent unbounded file growth
4. **Cache baseline** to speed up comparisons
5. **Parallelize configurations** in experiment_matrix.py for faster runs

## Related Documentation

- `EXPERIMENT_MATRIX.md` - Experiment system details
- `LATENCY_MEASUREMENT.md` - Latency tracking implementation
- `data/README.md` - Data file formats

## Future Enhancements

- [ ] Automatic remediation suggestions with code examples
- [ ] Integration with APM tools (Datadog, New Relic)
- [ ] A/B test automation based on regression results
- [ ] Machine learning for anomaly detection
- [ ] Performance budgets with hard limits
- [ ] Automatic rollback on critical regressions
- [ ] Distributed experiment execution
- [ ] Real-time dashboard (Streamlit/Grafana)
