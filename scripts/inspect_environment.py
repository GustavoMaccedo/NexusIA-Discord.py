#!/usr/bin/env python3


import platform
import shutil
import sys

import psutil

print(f"python={sys.version.split()[0]} arch={platform.machine()} cpus={psutil.cpu_count()}")
print(
    f"ram_total_mb={psutil.virtual_memory().total / 1e6:.0f} ram_avail_mb={psutil.virtual_memory().available / 1e6:.0f}"
)
print(f"disk_free_gb={shutil.disk_usage('.').free / 1e9:.1f}")
try:
    import torch

    print(f"torch={torch.__version__} cuda={torch.cuda.is_available()}")
except Exception as e:  # noqa: BLE001 — diagnóstico: qualquer falha vira linha de relatório
    print(f"torch ausente: {e}")
