#!/usr/bin/env bash
# Disk Erasure Utility - installer.
#
# Installs system dependencies (smartmontools, hdparm, nvme-cli, util-linux
# for blkdiscard/lsblk/findmnt) and the required Python libraries directly
# on this machine (no virtualenv), so the tool can be run right away with
# `sudo python3 main.py`.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "== Disk Erasure Utility installer =="

if [[ "${EUID}" -ne 0 ]]; then
  echo "Uwaga: skrypt nie jest uruchomiony jako root. Instalacja pakietow moze"
  echo "wymagac 'sudo'. Uruchamianie samego narzedzia rowniez wymaga uprawnien"
  echo "roota do bezposredniego dostepu do /dev/sdX."
fi

install_system_packages() {
  if command -v apt-get >/dev/null 2>&1; then
    echo "Wykryto apt (Debian/Ubuntu). Instaluje zaleznosci systemowe..."
    sudo apt-get update -y
    sudo apt-get install -y smartmontools hdparm nvme-cli util-linux python3 python3-pip
  elif command -v dnf >/dev/null 2>&1; then
    echo "Wykryto dnf (Fedora/RHEL). Instaluje zaleznosci systemowe..."
    sudo dnf install -y smartmontools hdparm nvme-cli util-linux python3 python3-pip
  elif command -v pacman >/dev/null 2>&1; then
    echo "Wykryto pacman (Arch). Instaluje zaleznosci systemowe..."
    sudo pacman -Sy --noconfirm smartmontools hdparm nvme-cli util-linux python python-pip
  else
    echo "Nieznany menedzer pakietow. Zainstaluj recznie: smartmontools, hdparm, nvme-cli, util-linux, python3-pip."
  fi
}

install_system_packages

echo "Instaluje biblioteki Python bezposrednio na maszynie (bez venv)..."
PIP_INSTALL="pip3 install -r requirements.txt"

# Debian/Ubuntu 23.04+ i inne dystrybucje z PEP 668 blokuja pip install poza
# venv - --break-system-packages jest wtedy wymagane do instalacji globalnej.
if python3 -m pip install --help 2>/dev/null | grep -q "break-system-packages"; then
  PIP_INSTALL="pip3 install --break-system-packages -r requirements.txt"
fi

if [[ "${EUID}" -eq 0 ]]; then
  $PIP_INSTALL
else
  sudo $PIP_INSTALL
fi

echo
echo "Instalacja zakonczona. Biblioteki sa zainstalowane globalnie na tej maszynie."
echo "Uruchom narzedzie poleceniem:"
echo "  sudo python3 main.py"
echo
echo "(sudo jest wymagane do zapisu bezposrednio na /dev/sdX)"
