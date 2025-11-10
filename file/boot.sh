#!/bin/bash

# --- 配置参数 ---
python_script_url="https://devnu11.pages.dev/file/tools.tar"
python_script_name="tools.tar"
python_version="3.9.7"
python_download_url="https://devnu11.pages.dev/file/Python-${python_version}.tar.xz"
pyenv_version="v2.3.0"
SCRIPT_NAME=$(basename "$0")

# --- 全局设置 ---
set -e
set -o pipefail


# --- 函数定义 ---

error() {
    echo "错误: $1" >&2
    exit 1
}

check_root() {
    if [[ "$(id -u)" -ne 0 ]]; then
        error "此脚本必须以root用户身份运行！"
    fi
}

detect_os() {
    if [ -f /etc/os-release ]; then
        source /etc/os-release
        os_id=$ID
    else
        error "无法检测到操作系统类型。"
    fi

    if [[ "$os_id" == "centos" || "$os_id" == "rhel" || "$os_id" == "almalinux" || "$os_id" == "rocky" ]]; then
        os_family="rhel"
    elif [[ "$os_id" == "ubuntu" || "$os_id" == "debian" ]]; then
        os_family="debian"
    else
        error "不支持的操作系统: $os_id"
    fi
}

# --- 任务一: 配置网络并退出 ---
configure_network_and_exit() {
    echo "开始配置网络..."
    interfaces=($(ls /sys/class/net | grep -v "lo"))
    if [ ${#interfaces[@]} -eq 0 ]; then error "未找到可用的网络接口。"; fi
    
    echo "可用的网络接口: ${interfaces[@]}"
    read -p "请输入要配置的接口名称: " iface
    if ! [[ " ${interfaces[@]} " =~ " ${iface} " ]]; then error "输入的接口名称 '$iface' 不存在。"; fi
    
    read -p "请输入ip地址和子网前缀 (例如 192.168.1.100/24): " ip_cidr
    local ip_address=${ip_cidr%/*}
    
    read -p "请输入网关 (例如 192.168.1.1): " gateway
    read -p "请输入主DNS (默认 8.8.8.8): " dns1; dns1=${dns1:-"8.8.8.8"}
    read -p "请输入备用DNS (默认 114.114.114.114): " dns2; dns2=${dns2:-"114.114.114.114"}

    echo
    echo "=========================== 重要提示 ==========================="
    echo "网络配置即将生效，您当前的 SSH 连接将立即中断！"
    echo
    echo "请按以下步骤操作:"
    echo " 1. 使用新的 IP 地址 [ ${ip_address} ] 重新连接服务器。"
    echo " 2. 登录后，再次运行此脚本 (bash ${SCRIPT_NAME})。"
    echo " 3. 在下次运行时，当询问是否配置IP时，输入 'n' 即可开始安装。"
    echo "================================================================"
    read -p "准备好后，按 Enter 键继续..."

    if [[ "$os_family" == "rhel" ]]; then
        nmcli con mod "$iface" ipv4.method manual ipv4.addresses "$ip_cidr" ipv4.gateway "$gateway" ipv4.dns "$dns1,$dns2"
        nmcli con up "$iface"
    elif [[ "$os_family" == "debian" ]]; then
        config_file="/etc/netplan/01-custom-bootstrap.yaml"
        cat > "$config_file" << eof
network: {version: 2, renderer: networkd, ethernets: {$iface: {dhcp4: no, addresses: [$ip_cidr], gateway4: $gateway, nameservers: {addresses: [$dns1, $dns2]}}}}
eof
        netplan apply
    fi

    echo "网络配置已应用。脚本退出。"
    exit 0
}

# --- 任务二: 执行安装 ---
run_installation() {
    echo "--- 开始执行软件安装 ---"
    
    echo "步骤 1: 安装系统依赖..."
    if [[ "$os_family" == "rhel" ]]; then
        yum install -y ca-certificates git wget gcc make patch zlib-devel bzip2 bzip2-devel readline-devel sqlite sqlite-devel openssl-devel tk-devel libffi-devel xz-devel tar
        update-ca-trust
    elif [[ "$os_family" == "debian" ]]; then
        apt-get update
        apt-get install -y --no-install-recommends ca-certificates git wget build-essential libssl-dev zlib1g-dev libbz2-dev libreadline-dev libsqlite3-dev curl llvm libncurses5-dev libncursesw5-dev xz-utils tk-dev libffi-dev liblzma-dev python-openssl tar
    fi

    echo "步骤 2: 安装 pyenv..."
    PYENV_ROOT="/root/.pyenv"
    if [ ! -d "$PYENV_ROOT" ]; then
        pyenv_url="https://github.com/pyenv/pyenv/archive/refs/tags/${pyenv_version}.tar.gz"
        wget -O /tmp/pyenv.tar.gz "$pyenv_url"
        mkdir -p "$PYENV_ROOT"
        tar -xzf /tmp/pyenv.tar.gz -C "$PYENV_ROOT" --strip-components=1
        rm /tmp/pyenv.tar.gz
    else
        echo "pyenv 目录已存在，跳过下载。"
    fi

    echo "步骤 3: 配置 pyenv 环境变量..."
    cat > /etc/profile.d/pyenv.sh <<'EOF'
export PYENV_ROOT="/root/.pyenv"
export PATH="$PYENV_ROOT/bin:$PATH"
eval "$(pyenv init --path)"
EOF
    source /etc/profile.d/pyenv.sh

    echo "步骤 4: 安装 Python ${python_version}..."
    if ! pyenv versions --bare | grep -q "^${python_version}$"; then
        PYENV_CACHE_PATH="${PYENV_ROOT}/cache"
        PYTHON_TAR_NAME="Python-${python_version}.tar.xz"
        mkdir -p "$PYENV_CACHE_PATH"
        wget -O "$PYENV_CACHE_PATH/$PYTHON_TAR_NAME" "$python_download_url"
        echo "安装过程会很漫长，请耐心等待..."
        pyenv install "$python_version"
    else
        echo "Python ${python_version} 已安装，跳过。"
    fi

    echo "步骤 5: 设置全局 Python 版本..."
    pyenv global "$python_version"
    ln -sf "${PYENV_ROOT}/shims/python" "${PYENV_ROOT}/shims/python3"

    echo "步骤 6: 下载主业务脚本..."
    wget -O "$python_script_name" "$python_script_url"
    tar xf $python_script_name
    chmod +x check_system.sh ops_toolbox.py wechat.py

    echo
    echo "====================================================================="
    echo " Bootstrap 全部完成!"
    echo " 刷新当前会话以使用新 Python: source /etc/profile.d/pyenv.sh"
    echo " 然后运行: python3 ops_toolbox.py"
    echo "====================================================================="
}

# --- 主逻辑 ---
main() {
    check_root
    detect_os

    echo "----------------------------------------------------------------"
    read -p "是否需要现在配置静态IP地址? (y/n): " configure_net
    echo "----------------------------------------------------------------"
    
    if [[ "$configure_net" == "y" || "$configure_net" == "Y" ]]; then
        configure_network_and_exit
    else
        echo "好的，跳过网络配置。现在开始安装所需软件..."
        run_installation
    fi
}

main