# TEMPLE INTEGRATION GUIDE — Sentinel Subsystem

## Purpose
Integrate the Sentinel into Temple modules, Memory Chamber, Timeline, and GuardianAI.

## How to Invoke the Sentinel
```python
from sentinel.sentinel_api import invoke_sentinel
invoke_sentinel("TempleModule", "instability detected")
