#!/usr/bin/env python3
"""
Self-Improvement System for AI Receptionist

Monitors critical files for changes, automatically runs experiments,
detects performance regressions, and provides optimization recommendations.

Usage:
    python self_improver.py

Features:
    - File watching (ai_engine.py, twilio_router.py)
    - Automatic experiment execution on changes
    - Regression detection (>20% latency increase)
    - Cost tracking and comparison
    - Optimization recommendations
    - Continuous monitoring mode
"""

import asyncio
import json
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler, FileModifiedEvent
except ImportError:
    print("Error: watchdog not installed. Run: pip install watchdog")
    sys.exit(1)


# Configuration
WATCHED_FILES = [
    "ai_receptionist/services/ai/gemini.py",
    "ai_receptionist/app/api/twilio.py",
]

EXPERIMENT_SCRIPT = "experiment_matrix.py"
RESULTS_FILE = "data/latency_matrix.json"
HISTORY_FILE = "data/experiment_history.jsonl"
REGRESSION_THRESHOLD = 0.20  # 20% increase triggers warning


class ExperimentResults:
    """Parse and analyze experiment results"""
    
    def __init__(self, filepath: str):
        self.filepath = filepath
        self.data = self._load()
        
    def _load(self) -> Dict:
        """Load results from JSON file"""
        if not os.path.exists(self.filepath):
            return {}
        
        with open(self.filepath, 'r') as f:
            return json.load(f)
    
    def get_aggregates(self) -> Dict[str, Dict]:
        """Extract aggregate metrics for each configuration"""
        if not self.data or 'results' not in self.data:
            return {}
        
        aggregates = {}
        for result in self.data['results']:
            config_name = result['aggregate']['config_name']
            aggregates[config_name] = {
                'avg_ai_latency_ms': result['aggregate']['avg_ai_latency_ms'],
                'min_ai_latency_ms': result['aggregate']['min_ai_latency_ms'],
                'max_ai_latency_ms': result['aggregate']['max_ai_latency_ms'],
                'avg_total_latency_ms': result['aggregate']['avg_total_latency_ms'],
                'total_tokens': result['aggregate']['total_tokens'],
                'total_cost_usd': result['aggregate']['total_cost_usd'],
                'success_count': result['aggregate']['success_count'],
                'failure_count': result['aggregate']['failure_count'],
            }
        return aggregates
    
    def get_metadata(self) -> Dict:
        """Extract experiment metadata"""
        if not self.data or 'experiment_metadata' not in self.data:
            return {}
        return self.data['experiment_metadata']


class RegressionDetector:
    """Detect performance regressions between experiments"""
    
    def __init__(self, threshold: float = REGRESSION_THRESHOLD):
        self.threshold = threshold
    
    def compare(
        self, 
        baseline: Dict[str, Dict], 
        current: Dict[str, Dict]
    ) -> Tuple[bool, List[Dict]]:
        """
        Compare two experiment results
        
        Returns:
            (has_regression, regression_details)
        """
        regressions = []
        
        for config_name in current.keys():
            if config_name not in baseline:
                continue
            
            baseline_latency = baseline[config_name]['avg_ai_latency_ms']
            current_latency = current[config_name]['avg_ai_latency_ms']
            
            if baseline_latency == 0:
                continue
            
            percent_change = (current_latency - baseline_latency) / baseline_latency
            
            if percent_change > self.threshold:
                regressions.append({
                    'config': config_name,
                    'baseline_latency_ms': baseline_latency,
                    'current_latency_ms': current_latency,
                    'percent_increase': percent_change * 100,
                    'delta_ms': current_latency - baseline_latency,
                    'baseline_cost': baseline[config_name]['total_cost_usd'],
                    'current_cost': current[config_name]['total_cost_usd'],
                })
        
        return len(regressions) > 0, regressions
    
    def generate_recommendations(self, regressions: List[Dict]) -> List[str]:
        """Generate optimization recommendations based on regressions"""
        recommendations = []
        
        for reg in regressions:
            config = reg['config']
            delta = reg['delta_ms']
            percent = reg['percent_increase']
            
            recommendations.append(
                f"⚠️  {config}: +{delta:.1f}ms ({percent:.1f}% increase)"
            )
            
            # Specific recommendations based on configuration
            if 'rag' in config.lower():
                recommendations.append(
                    f"   → Check RAG context size and retrieval efficiency"
                )
            
            if 'full_stack' in config.lower() or 'enhanced' in config.lower():
                recommendations.append(
                    f"   → Review prompt complexity and token count"
                )
            
            if delta > 200:
                recommendations.append(
                    f"   → Consider caching or async optimizations"
                )
            
            # Cost impact
            cost_delta = reg['current_cost'] - reg['baseline_cost']
            if cost_delta > 0.0001:
                recommendations.append(
                    f"   → Cost increased by ${cost_delta:.6f} (+{(cost_delta/reg['baseline_cost']*100):.1f}%)"
                )
        
        return recommendations


class ExperimentHistory:
    """Manage experiment history"""
    
    def __init__(self, filepath: str):
        self.filepath = filepath
        self._ensure_file()
    
    def _ensure_file(self):
        """Create history file if it doesn't exist"""
        os.makedirs(os.path.dirname(self.filepath), exist_ok=True)
        if not os.path.exists(self.filepath):
            with open(self.filepath, 'w') as f:
                pass  # Create empty file
    
    def append(self, results: Dict[str, Dict], metadata: Dict, trigger: str):
        """Append experiment results to history"""
        entry = {
            'timestamp': datetime.now().isoformat(),
            'trigger': trigger,
            'model': metadata.get('model_name', 'unknown'),
            'aggregates': results,
        }
        
        with open(self.filepath, 'a') as f:
            f.write(json.dumps(entry) + '\n')
    
    def get_latest(self) -> Optional[Dict[str, Dict]]:
        """Get latest experiment aggregates"""
        if not os.path.exists(self.filepath):
            return None
        
        with open(self.filepath, 'r') as f:
            lines = f.readlines()
        
        if not lines:
            return None
        
        latest = json.loads(lines[-1])
        return latest.get('aggregates', {})
    
    def get_all(self) -> List[Dict]:
        """Get all experiment history"""
        if not os.path.exists(self.filepath):
            return []
        
        history = []
        with open(self.filepath, 'r') as f:
            for line in f:
                if line.strip():
                    history.append(json.loads(line))
        return history


class CodeChangeHandler(FileSystemEventHandler):
    """Handle file system events for watched files"""
    
    def __init__(self, callback):
        self.callback = callback
        self.last_modified = {}
        self.debounce_seconds = 2  # Prevent multiple triggers
    
    def on_modified(self, event: FileModifiedEvent):
        if event.is_directory:
            return
        
        # Check if this is a watched file
        filepath = event.src_path
        if not any(watched in filepath for watched in WATCHED_FILES):
            return
        
        # Debounce: ignore if modified too recently
        now = time.time()
        if filepath in self.last_modified:
            if now - self.last_modified[filepath] < self.debounce_seconds:
                return
        
        self.last_modified[filepath] = now
        
        # Trigger callback
        print(f"\n📝 Detected change in: {os.path.basename(filepath)}")
        self.callback(filepath)


class SelfImprover:
    """Main self-improvement orchestrator"""
    
    def __init__(self):
        self.detector = RegressionDetector()
        self.history = ExperimentHistory(HISTORY_FILE)
        self.running = False
    
    def run_experiment(self, trigger: str = "manual") -> bool:
        """Execute experiment_matrix.py and capture results"""
        print(f"\n🔬 Running experiments (trigger: {trigger})...")
        print(f"⏱️  This will take 30-90 seconds...")
        
        try:
            result = subprocess.run(
                [sys.executable, EXPERIMENT_SCRIPT],
                capture_output=True,
                text=True,
                timeout=180,  # 3 minute timeout
            )
            
            if result.returncode != 0:
                print(f"❌ Experiment failed:")
                print(result.stderr)
                return False
            
            print("✅ Experiments completed")
            return True
            
        except subprocess.TimeoutExpired:
            print("❌ Experiment timed out after 3 minutes")
            return False
        except Exception as e:
            print(f"❌ Error running experiments: {e}")
            return False
    
    def analyze_results(self, trigger: str = "manual"):
        """Analyze latest results and detect regressions"""
        print("\n📊 Analyzing results...")
        
        # Load current results
        current_results = ExperimentResults(RESULTS_FILE)
        current_aggregates = current_results.get_aggregates()
        current_metadata = current_results.get_metadata()
        
        if not current_aggregates:
            print("⚠️  No results to analyze")
            return
        
        # Get baseline (previous run)
        baseline_aggregates = self.history.get_latest()
        
        # Save current to history
        self.history.append(current_aggregates, current_metadata, trigger)
        
        # Print current metrics
        print("\n📈 Current Metrics:")
        print("─" * 80)
        for config, metrics in current_aggregates.items():
            print(f"{config:25} {metrics['avg_ai_latency_ms']:8.1f}ms  "
                  f"{metrics['total_tokens']:6d} tokens  "
                  f"${metrics['total_cost_usd']:.6f}")
        
        # Compare with baseline if available
        if baseline_aggregates:
            print("\n🔍 Regression Analysis:")
            print("─" * 80)
            
            has_regression, regressions = self.detector.compare(
                baseline_aggregates, 
                current_aggregates
            )
            
            if has_regression:
                print("⚠️  PERFORMANCE REGRESSIONS DETECTED:")
                print()
                recommendations = self.detector.generate_recommendations(regressions)
                for rec in recommendations:
                    print(rec)
                print()
                print(f"🎯 Regression threshold: {REGRESSION_THRESHOLD * 100}%")
            else:
                print("✅ No significant regressions detected")
                
                # Show improvements
                improvements = []
                for config in current_aggregates.keys():
                    if config in baseline_aggregates:
                        baseline_lat = baseline_aggregates[config]['avg_ai_latency_ms']
                        current_lat = current_aggregates[config]['avg_ai_latency_ms']
                        
                        if current_lat < baseline_lat:
                            delta = baseline_lat - current_lat
                            percent = (delta / baseline_lat) * 100
                            improvements.append(
                                f"   ✓ {config}: -{delta:.1f}ms ({percent:.1f}% faster)"
                            )
                
                if improvements:
                    print("\n💚 Performance Improvements:")
                    for imp in improvements:
                        print(imp)
        else:
            print("\n📌 Baseline established (no previous results to compare)")
        
        print("\n" + "─" * 80)
    
    def on_code_change(self, filepath: str):
        """Callback when watched file changes"""
        if not self.running:
            return
        
        trigger = f"file_change: {os.path.basename(filepath)}"
        
        # Run experiment
        if self.run_experiment(trigger):
            # Analyze results
            self.analyze_results(trigger)
        else:
            print("⚠️  Skipping analysis due to experiment failure")
    
    def watch(self):
        """Start watching files for changes"""
        print("👁️  Self-Improvement System Started")
        print("=" * 80)
        print(f"Watching files:")
        for filepath in WATCHED_FILES:
            full_path = os.path.abspath(filepath)
            exists = "✓" if os.path.exists(full_path) else "✗"
            print(f"  {exists} {filepath}")
        print(f"\nRegression threshold: {REGRESSION_THRESHOLD * 100}%")
        print(f"Results: {RESULTS_FILE}")
        print(f"History: {HISTORY_FILE}")
        print("\nPress Ctrl+C to stop")
        print("=" * 80)
        
        # Run initial experiment
        print("\n🚀 Running initial baseline experiment...")
        if self.run_experiment("initial_baseline"):
            self.analyze_results("initial_baseline")
        
        # Set up file watcher
        event_handler = CodeChangeHandler(self.on_code_change)
        observer = Observer()
        
        # Watch the ai_receptionist directory
        watch_path = os.path.abspath("ai_receptionist")
        observer.schedule(event_handler, watch_path, recursive=True)
        
        self.running = True
        observer.start()
        
        try:
            print("\n👀 Monitoring for changes...")
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n\n🛑 Stopping self-improvement system...")
            self.running = False
            observer.stop()
        
        observer.join()
        print("✅ Shutdown complete")


def main():
    """Main entry point"""
    # Check prerequisites
    if not os.path.exists(EXPERIMENT_SCRIPT):
        print(f"❌ Error: {EXPERIMENT_SCRIPT} not found")
        sys.exit(1)
    
    # Ensure data directory exists
    os.makedirs("data", exist_ok=True)
    
    # Start self-improver
    improver = SelfImprover()
    improver.watch()


if __name__ == "__main__":
    main()
