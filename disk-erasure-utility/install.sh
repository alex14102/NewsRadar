#!/usr/bin/env bash
# Disk Erasure Utility - installer.
#
# Installs system dependencies (smartmontools, hdparm, nvme-cli, util-linux
# for blkdiscard/lsblk/findmnt) where possible, then sets up a Python
# virtual environment with the required packages.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "== Disk Erasure Utility installer =="

if [[ "${EUID}" -ne 0 ]]; then
  echo "Uwaga: skrypt nie jest uruchomiony jako root. Instalacja pakietow systemowych"
  echo "moze wymagac 'sudo'. Uruchamianie samego narzedzia rowniez wymaga uprawnien"
  echo "roota do bezposredniego dostepu do /dev/sdX."
fi

install_system_packages() {
  if command -v apt-get >/dev/null 2>&1; then
    echo "Wykryto apt (Debian/Ubuntu). Instaluje zaleznosci systemowe..."
    sudo apt-get update -y
    sudo apt-get install -y smartmontools hdparm nvme-cli util-linux python3-venv python3-pip
  elif command -v dnf >/dev/null 2>&1; then
    echo "Wykryto dnf (Fedora/RHEL). Instaluje zaleznosci systemowe..."
    sudo dnf install -y smartmontools hdparm nvme-cli util-linux python3
  elif command -v pacman >/dev/null 2>&1; then
    echo "Wykryto pacman (Arch). Instaluje zaleznosci systemowe..."
    sudo pacman -Sy --noconfirm smartmontools hdparm nvme-cli util-linux python
  else
    echo "Nieznany menedzer pakietow. Zainstaluj recznie: smartmontools, hdparm, nvme-cli, util-linux."
  fi
}

install_system_packages

echo "Tworze srodowisko wirtualne Python (.venv)..."
python3 -m venv .venv
# shellcheck disable=SC1091
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

echo
echo "Instalacja zakonczona."
echo "Uruchom narzedzie poleceniem:"
echo "  source .venv/bin/activate"
echo "  sudo .venv/bin/python main.py"
echo
echo "(sudo jest wymagane do zapisu bezposrednio na /dev/sdX)"
