
import importlib.util


class ScalingCriterion:
    def max_workers(self) -> int:
        raise NotImplementedError


class TimeCriterion(ScalingCriterion):
    def __init__(
        self,
        day_workers=2,
        night_workers=12,
        night_start=22,
        night_end=3,
        tz="Asia/Kolkata",
    ):
        if not importlib.util.find_spec("pytz"):
            raise ImportError("TimeCriterion requires 'pytz' package. Install with: pip install adaptive-executor[time]")
        
        import pytz
        self.day_workers = day_workers
        self.night_workers = night_workers
        self.night_start = night_start
        self.night_end = night_end
        self.tz = pytz.timezone(tz)

    def max_workers(self):
        from datetime import datetime
        h = datetime.now(self.tz).hour
        if h >= self.night_start or h < self.night_end:
            return self.night_workers
        return self.day_workers


class CpuCriterion(ScalingCriterion):
    def __init__(self, threshold=75):
        if not importlib.util.find_spec("psutil"):
            raise ImportError("CpuCriterion requires 'psutil' package. Install with: pip install adaptive-executor[cpu]")
        
        self.threshold = threshold

    def max_workers(self):
        import psutil
        return 2 if psutil.cpu_percent() > self.threshold else 12


class MemoryCriterion(ScalingCriterion):
    def __init__(self, threshold=80):
        if not importlib.util.find_spec("psutil"):
            raise ImportError("MemoryCriterion requires 'psutil' package. Install with: pip install adaptive-executor[cpu]")
        
        self.threshold = threshold

    def max_workers(self):
        import psutil
        return 2 if psutil.virtual_memory().percent > self.threshold else 12
