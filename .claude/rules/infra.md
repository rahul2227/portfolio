---
globs: deploy/**
---

# Infrastructure Rules

- Always validate nginx config with `nginx -t` before applying
- systemd services: `Restart=on-failure`, resource limits via `MemoryMax`
- Comment every config block explaining its purpose
- Run services as user `rahser`, not root
- Check `systemctl status` after restarts to confirm services are running
- Monitor RAM with `free -h` — alert if available drops below 500MB
