# Aigen RPi Zero 2W (ssh168.cfaig2vie.uk) — Change Log

## 2026-06-07 — Memory hardening after unexpected reboot

### Root cause
Pi performed scheduled 2AM cron reboot (`0 2 * * * root /sbin/reboot`). Not a crash. User power-cycled again at ~09:30 after finding it unresponsive during reboot window.

### Changes applied

#### 1. Persistent journal enabled
- Created `/var/log/journal/` so `journalctl -b -1` survives reboots
- Command: `sudo mkdir -p /var/log/journal && sudo systemd-tmpfiles --create --prefix /var/log/journal && sudo systemctl restart systemd-journald`

#### 2. Memory cgroups enabled
- Added `cgroup_enable=memory cgroup_memory=1` to `/boot/firmware/cmdline.txt`
- Required for Docker to enforce per-container memory limits

#### 3. Swappiness lowered
- Changed `vm.swappiness` from 60 → 10
- Persisted in `/etc/sysctl.conf`
- Reduces swap thrashing on 416MB device

#### 4. Docker container memory limits added
| Container   | Limit | Compose file |
|-------------|-------|--------------|
| portainer   | 150MB | `/home/pi/dockersource/portainer/docker-compose.yml` |
| cloudflared |  64MB | `/home/pi/dockersource/cloudflared/docker-compose.yml` |
| dozzle      |  80MB | `/home/pi/dockersource/dozzle/docker-compose.yml` |

Total cap: 294MB — leaves ~120MB headroom for OS on 416MB RAM.

### Verified
- `docker inspect` confirms limits baked into container config
- `restart=unless-stopped` — limits survive 2AM reboot
- Next scheduled reboot: Mon 2026-06-09 02:00 CEST
