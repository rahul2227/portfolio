---
name: status
description: Check the health of all portfolio services, system resources, and current public URL on the Raspberry Pi.
disable-model-invocation: true
allowed-tools: Bash
---

Check the status of the portfolio deployment on the Raspberry Pi.

## Checks to perform

1. **Service status** — check each service and report active/inactive/failed:
   ```bash
   systemctl is-active portfolio-backend nginx redis-server cloudflared-portfolio
   ```

2. **Backend health endpoint**:
   ```bash
   curl -sf http://127.0.0.1:8000/health 2>&1 || echo "Backend not responding"
   ```

3. **Frontend serving**:
   ```bash
   curl -sf -o /dev/null -w "%{http_code}" http://localhost/ || echo "Frontend not responding"
   ```

4. **Public tunnel URL**:
   ```bash
   journalctl -u cloudflared-portfolio --no-pager -n 50 | grep -o 'https://.*trycloudflare.com' | tail -1
   ```

5. **System resources**:
   ```bash
   echo "=== RAM ===" && free -h
   echo "=== Disk ===" && df -h /
   echo "=== CPU Temp ===" && cat /sys/class/thermal/thermal_zone0/temp | awk '{printf "%.1f°C\n", $1/1000}'
   echo "=== Uptime ===" && uptime
   ```

6. **Recent errors** (last 10 minutes):
   ```bash
   journalctl -u portfolio-backend --since "10 minutes ago" --priority=err --no-pager 2>&1 | tail -20
   ```

Present results as a clear status dashboard.
