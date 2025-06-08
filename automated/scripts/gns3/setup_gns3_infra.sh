
# ============================================
# SCRIPT DE INSTALAÇÃO - INFRAESTRUTURA GNS3
# Para suportar Docker + GNS3 + Dynamips
# Ambiente: Ubuntu (dentro do OrbStack ou VM)
# Data: 2025-05-24
# ============================================

# 1. Atualizar pacotes
sudo apt update && sudo apt upgrade -y

# 2. Instalar dependências básicas
sudo apt install -y \
    curl wget unzip nano net-tools software-properties-common \
    apt-transport-https ca-certificates gnupg lsb-release

# 3. Instalar Docker
sudo apt remove docker docker-engine docker.io containerd runc -y
sudo apt install -y docker.io
sudo systemctl enable docker
sudo systemctl start docker

# 4. Adicionar teu user ao grupo 'docker'
sudo usermod -aG docker $USER

# 5. Instalar Dynamips
sudo apt install -y dynamips

# 6. Verificar status do Docker e Dynamips
docker --version
dynamips --version

# 7. Instalar GNS3 Server e GUI (se necessário)
# (Recomenda-se usar GNS3 GUI no host e apenas o Server aqui)
sudo add-apt-repository ppa:gns3/ppa -y
sudo apt update
sudo apt install -y gns3-server gns3-gui

# 8. Permitir acesso do GNS3 ao Docker
sudo chmod 666 /var/run/docker.sock

# 9. Iniciar GNS3 Server manualmente (se necessário)
gns3server --host 0.0.0.0

# 10. Reinicia para aplicar grupos
echo " INSTALAÇÃO COMPLETA! Agora reinicia a máquina: sudo reboot"
