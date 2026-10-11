import psutil


def usage() -> dict:
    p = psutil.Process()
    return {"rss_mb": p.memory_info().rss / 1e6, "cpu_pct": p.cpu_percent(interval=0.1)}
