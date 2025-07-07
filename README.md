# Raspberry Pi Home Server Automation

This project automates the setup and management of a home server on a Raspberry Pi using Ansible. It includes playbooks for installing Docker, deploying Home Assistant (with Zigbee and Traefik integration), setting up Tailscale for remote access, and managing user directory backups/restores.

## Project Structure

```
group_vars/
  all.public.yml      # Example config variables (rename to all.yml and fill in)
playbooks/
  install_docker.yml          # Installs Docker and dependencies
  deploy_home_assistant.yml   # Deploys Home Assistant with Zigbee and Traefik
  setup_tailscale.yml         # Installs and configures Tailscale VPN
  backup_user_directory.yml   # Backs up the user directory
  restore_user_directory.yml  # Restores the user directory from backup
templates/
  home_assistent_docker_compose.yml.j2  # Docker Compose template for Home Assistant
hosts.ini                # Ansible inventory (edit for your setup)
```

---

## Technologies Used

- **Ansible**: Automation and orchestration
- **Docker**: Containerization for Home Assistant
- **Home Assistant**: Home automation platform
- **Tailscale**: Zero-config VPN for secure remote access
- **Traefik**: Reverse proxy (network created, not configured here)
- **Zigbee**: USB stick integration for smart home devices

---

## Setup Instructions

### 1. Prerequisites

- Raspberry Pi running Debian-based OS (e.g., Raspberry Pi OS)
- Ansible installed on your control machine (not the Pi)
- SSH access to the Pi
- (Optional) Zigbee USB stick for Home Assistant

#### Install Ansible (on your control machine):

```sh
pip install ansible
```

---

### 2. Configure Inventory and Variables

#### Edit `hosts.ini`:

Set your Raspberry Pi's hostname and user:
```
[raspberrypi]
basichub.local ansible_user=luha
```
Replace `basichub.local` and `luha` as needed.

#### Configure variables:

Copy and edit the example config:
```sh
cp group_vars/all.public.yml group_vars/all.yml
```
Edit `group_vars/all.yml` and set:
- `domain`, `email`, `timezone`
- `tailscale_auth_key` (get from Tailscale admin panel)
- `backup_base_dir` (where backups are stored on your control machine)

---

### 3. Install Docker on the Raspberry Pi

```sh
ansible-playbook -i hosts.ini playbooks/install_docker.yml
```

---

### 4. Set Up Tailscale VPN

```sh
ansible-playbook -i hosts.ini playbooks/setup_tailscale.yml
```
- Requires a valid `tailscale_auth_key` in your variables.

---

### 5. Deploy Home Assistant (with Zigbee and Traefik)

Plug in your Zigbee USB stick before running.

```sh
ansible-playbook -i hosts.ini playbooks/deploy_home_assistant.yml
```
- This will:
  - Create a Docker network for Traefik (`traefik_net`)
  - Set up Home Assistant with Docker Compose
  - Detect and configure the Zigbee stick
  - Ensure user permissions for Zigbee

---

### 6. Backup and Restore User Directory

#### Backup:

```sh
ansible-playbook -i hosts.ini playbooks/backup_user_directory.yml
```
- Saves a timestamped tarball of `/home/<ansible_user>` to `backup_base_dir` on your control machine.

#### Restore:

```sh
ansible-playbook -i hosts.ini playbooks/restore_user_directory.yml
```
- Restores the latest backup by default, or specify a backup file with `-e "backup_file=/path/to/backup.tar.gz"`

---

## Home Assistant Docker Compose Template

The template (`templates/home_assistent_docker_compose.yml.j2`) configures Home Assistant with:
- Persistent config in `/home/<ansible_user>/homeassistant`
- Zigbee device passthrough
- Timezone from Ansible facts
- Port 8123 exposed
- Connected to the external `traefik_net` Docker network

---

## Notes

- All playbooks are idempotent and safe to re-run.
- For Traefik reverse proxy, you must configure Traefik separately to use the `traefik_net` Docker network.
- Tailscale setup will skip if already configured.
- Backups are stored on the control machine, not the Pi.

---

## Quick Start (All-in-One)

```sh
# 1. Install Docker
ansible-playbook -i hosts.ini playbooks/install_docker.yml

# 2. Set up Tailscale
ansible-playbook -i hosts.ini playbooks/setup_tailscale.yml

# 3. Deploy Home Assistant
ansible-playbook -i hosts.ini playbooks/deploy_home_assistant.yml

# 4. Backup user directory
ansible-playbook -i hosts.ini playbooks/backup_user_directory.yml

# 5. Restore user directory (if needed)
ansible-playbook -i hosts.ini playbooks/restore_user_directory.yml
```

---

## Troubleshooting

- Ensure your Pi is reachable via SSH and the user has sudo privileges.
- For Zigbee, check the USB stick is detected (`/dev/serial/by-id/`).
- For Tailscale, ensure your auth key is valid and not expired.
