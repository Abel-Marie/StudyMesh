from datetime import datetime
from collections import defaultdict

class MetricsCollector:
    """Collects and tracks metrics for the planner."""
    
    def __init__(self):
        self.metrics = defaultdict(list)
        self.counters = defaultdict(int)
    
    def track_metric(self, metric_name, value):
        """Track a metric value."""
        self.metrics[metric_name].append({
            "timestamp": datetime.now().isoformat(),
            "value": value
        })
    
    def increment_counter(self, counter_name):
        """Increment a counter."""
        self.counters[counter_name] += 1
    
    def get_metric_average(self, metric_name):
        """Get average value for a metric."""
        if metric_name not in self.metrics or not self.metrics[metric_name]:
            return 0
        
        values = [m['value'] for m in self.metrics[metric_name]]
        return sum(values) / len(values)
    
    def get_counter(self, counter_name):
        """Get counter value."""
        return self.counters.get(counter_name, 0)
    
    def get_all_metrics(self):
        """Get all metrics summary."""
        summary = {}
        
        for metric_name, values in self.metrics.items():
            if values:
                summary[metric_name] = {
                    "count": len(values),
                    "average": sum([v['value'] for v in values]) / len(values),
                    "latest": values[-1]['value']
                }
        
        for counter_name, value in self.counters.items():
            summary[f"{counter_name}_count"] = value
        
        return summary
