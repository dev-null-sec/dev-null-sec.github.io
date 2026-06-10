from ipaddress import ip_address, ip_network
import curses
import locale
import os
import sys
import subprocess
import shutil

locale.setlocale(locale.LC_ALL, '')

# ============================================
# 运维工具箱 - 让Linux服务器管理更简单
# ============================================


# --------------------------------------------
# 第一部分：基础工具函数
# 这些函数是最底层的，用来执行命令和检查系统
# --------------------------------------------

def run_system_command(command_list, work_directory=None):
    """
    执行一条系统命令，并显示执行结果
    
    这个函数就像一个"命令执行器"：
    - 你告诉它要执行什么命令
    - 它会帮你执行，并告诉你成功还是失败
    
    参数说明：
        command_list: 命令列表，比如 ['ls', '-l'] 表示执行 ls -l 命令
        work_directory: 在哪个文件夹里执行这个命令（可选，默认是当前文件夹）
    
    返回值：
        如果命令执行成功，返回 True
        如果命令执行失败，返回 False
    """
    try:
        # 先把命令列表变成字符串，方便打印给用户看
        command_text = ' '.join(command_list)
        
        # 执行这个命令，check=True 表示如果命令失败就抛出错误
        subprocess.run(command_list, check=True, cwd=work_directory)
        
        # 如果执行到这里，说明命令执行成功了
        return True
        
    except FileNotFoundError:
        # 这个错误表示：命令对应的程序没有安装
        # 比如你想执行 nginx，但系统里没装 nginx
        program_name = command_list[0]
        print(f"[!] 错误: 找不到命令 '{program_name}'，请检查这个程序是否已安装")
        return False
        
    except subprocess.CalledProcessError:
        # 这个错误表示：命令执行了，但是失败了
        # 比如你想删除一个不存在的文件
        print(f"[!] 错误: 命令 '{command_text}' 执行失败")
        return False


def check_command_exists(command_name):
    """
    检查某个命令是否存在（即程序是否已安装）
    
    就像问系统："你认识这个命令吗？"
    
    参数说明：
        command_name: 命令名称，比如 'nginx'、'docker' 等
    
    返回值：
        如果命令存在，返回 True
        如果命令不存在，返回 False
    """
    try:
        # 使用 which 命令查找这个程序在哪里
        # 如果找到了，返回码是0；找不到，返回码不是0
        result = subprocess.run(
            ['which', command_name],
            stdout=subprocess.DEVNULL,  # 不显示输出
            stderr=subprocess.DEVNULL   # 不显示错误
        )
        return result.returncode == 0
        
    except Exception:
        # 如果出现任何错误，就认为命令不存在
        return False


def check_if_linux_system():
    """
    检查当前系统是不是 Linux 系统
    
    这个函数会：
    1. 检查是不是 Linux
    2. 检查是不是 root 用户（管理员权限）
    
    如果不满足条件，程序会直接退出
    """
    # 第一步：检查操作系统类型
    print("[*] 正在检查操作系统类型...")
    if not sys.platform.startswith('linux'):
        print('[!] 错误：当前系统不是Linux系统')
        print('[!] 这个工具箱只能在Linux系统上运行')
        sys.exit(1)  # 退出程序
    print("[OK] 系统检查通过：这是一个 Linux 系统")
    
    # 第二步：检查用户权限（是否是root用户）
    print("[*] 正在检查用户权限...")
    current_user_id = os.geteuid()  # 获取当前用户的ID
    if current_user_id != 0:  # root用户的ID是0
        print('[!] 错误：当前用户不是root用户')
        print('[!] 请使用 sudo 或切换到 root 用户后再运行')
        sys.exit(1)  # 退出程序
    print("[OK] 权限检查通过：当前是 root 用户")


def read_system_info():
    """
    读取Linux系统的详细信息
    
    这个函数会读取 /etc/os-release 文件，这个文件里保存了系统的信息，
    比如是 Ubuntu 还是 CentOS，版本号是多少等等
    
    返回值：
        返回一个字典（就像一个信息盒子），里面包含：
        - system_type: 系统类型（如 'ubuntu', 'centos', 'rocky'）
        - system_version: 系统版本（如 '20.04', '8'）
        - system_codename: 系统代号（如 'focal', 'jammy'）
        - system_name: 系统完整名称（如 'Ubuntu 20.04 LTS'）
        - system_family: 系统家族（'debian' 或 'redhat'）
        - package_manager: 包管理器（'apt' 或 'yum' 或 'dnf'）
    """
    print('[*] 正在读取系统信息...')
    
    try:
        # 创建一个空的字典，用来存放从文件读取的信息
        os_release_data = {}
        
        # 打开 /etc/os-release 文件
        with open('/etc/os-release') as file:
            # 一行一行地读取文件内容
            for line in file:
                # 每一行格式是：KEY=VALUE
                # 比如：ID=ubuntu
                if '=' in line:
                    # 把这一行按照等号分成两部分
                    key, value = line.strip().split('=', 1)
                    # 把值两边的引号去掉，然后保存到字典里
                    os_release_data[key] = value.strip().strip('"')
        
        # 从字典里取出我们需要的信息
        system_type = os_release_data.get('ID', 'unknown')
        system_version = os_release_data.get('VERSION_ID', 'unknown')
        system_codename = os_release_data.get('VERSION_CODENAME', 'unknown')
        system_name = os_release_data.get('PRETTY_NAME', 'unknown')
        
        # 打印出来给用户看
        print(f'[OK] 系统类型: {system_type}')
        print(f'[OK] 系统版本: {system_version}')
        print(f'[OK] 系统代号: {system_codename}')
        print(f'[OK] 系统名称: {system_name}')
        
        # 判断这个系统属于哪个家族，使用什么包管理器
        system_info = detect_system_family(system_type, system_version, system_name)
        system_info['system_type'] = system_type
        system_info['system_version'] = system_version
        system_info['system_codename'] = system_codename
        system_info['system_name'] = system_name
        
        return system_info
        
    except FileNotFoundError:
        print('[!] 错误：找不到 /etc/os-release 文件')
        print('[!] 无法确定系统信息')
        sys.exit(1)
        
    except Exception as error:
        print(f'[!] 读取系统信息时出错: {error}')
        sys.exit(1)


def detect_system_family(system_type, system_version, system_name):
    """
    判断Linux系统属于哪个家族，并确定使用什么包管理器
    
    Linux系统主要分两大家族：
    1. Debian家族：使用 apt 包管理器（Ubuntu、Debian等）
    2. RedHat家族：使用 yum 或 dnf 包管理器（CentOS、Rocky、Alma等）
    
    参数说明：
        system_type: 系统类型
        system_version: 系统版本
        system_name: 系统完整名称
    
    返回值：
        返回一个字典，包含：
        - system_family: 系统家族（'debian' 或 'redhat'）
        - package_manager: 包管理器名称
        - is_supported: 是否支持自动化操作
    """
    # 先把系统类型转成小写，方便比较
    system_type_lower = system_type.lower()
    
    # 判断是 Debian 家族还是 RedHat 家族
    # Debian家族：Ubuntu、Debian、Linux Mint等
    debian_family = ['ubuntu', 'debian', 'linuxmint', 'pop']
    
    # RedHat家族：CentOS、Rocky、AlmaLinux、Fedora、RHEL等
    redhat_family = ['centos', 'rocky', 'almalinux', 'rhel', 'fedora', 'ol']
    
    if system_type_lower in debian_family:
        # 这是 Debian 家族，使用 apt 包管理器
        print('[OK] 识别为 Debian 系列系统，使用 apt 包管理器')
        return {
            'system_family': 'debian',
            'package_manager': 'apt',
            'is_supported': True
        }
        
    elif system_type_lower in redhat_family:
        # 这是 RedHat 家族
        # CentOS 8 / Rocky 8 / Alma 8 及以上使用 dnf
        # CentOS 7 及以下使用 yum
        print('[OK] 识别为 RedHat 系列系统')
        
        # 判断使用 yum 还是 dnf
        try:
            version_number = int(system_version.split('.')[0])
            if version_number >= 8:
                package_manager = 'dnf'
                print(f'[OK] 系统版本 >= 8，使用 dnf 包管理器')
            else:
                package_manager = 'yum'
                print(f'[OK] 系统版本 < 8，使用 yum 包管理器')
        except:
            # 如果无法判断版本，尝试检查 dnf 是否存在
            if check_command_exists('dnf'):
                package_manager = 'dnf'
            else:
                package_manager = 'yum'
        
        return {
            'system_family': 'redhat',
            'package_manager': package_manager,
            'is_supported': True
        }
    else:
        # 不认识的系统
        print(f'[!] 警告：系统类型 {system_type} 可能不被完全支持')
        print('[!] 程序会尝试继续运行，但可能会遇到问题')
        return {
            'system_family': 'unknown',
            'package_manager': 'unknown',
            'is_supported': False
        }


# --------------------------------------------
# 第二部分：包管理器统一接口
# 不同的Linux系统用不同的包管理器，这里统一封装
# --------------------------------------------

class PackageManager:
    """
    包管理器类 - 让不同Linux系统用同样的方式安装软件
    
    就像一个"翻译器"：
    - Ubuntu 用 apt install
    - CentOS 用 yum install 或 dnf install
    - 我们只需要说"安装某个软件"，它会自动选择正确的命令
    """
    
    def __init__(self, system_info):
        """
        初始化包管理器
        
        参数说明：
            system_info: 系统信息字典（从 read_system_info 函数获取）
        """
        self.system_info = system_info
        self.package_manager = system_info['package_manager']
        self.system_family = system_info['system_family']
        self.system_type = system_info['system_type']
    
    def install_packages(self, package_list):
        """
        安装软件包
        
        参数说明：
            package_list: 要安装的软件列表，比如 ['vim', 'wget', 'git']
        
        返回值：
            安装成功返回 True，失败返回 False
        """
        print(f"[*] 准备安装软件: {', '.join(package_list)}")
        
        if self.package_manager == 'apt':
            # Debian 家族：先更新索引，再安装
            print("[*] 正在更新软件包索引...")
            if not run_system_command(['apt', 'update']):
                return False
            print("[*] 正在安装软件...")
            return run_system_command(['apt', 'install', '-y'] + package_list)
            
        elif self.package_manager in ['yum', 'dnf']:
            # RedHat 家族：直接安装（yum/dnf 会自动处理依赖）
            print("[*] 正在安装软件...")
            return run_system_command([self.package_manager, 'install', '-y'] + package_list)
        else:
            print(f"[!] 错误：不支持的包管理器 {self.package_manager}")
            return False


# --------------------------------------------
# 第三部分：网络配置功能
# 帮助用户设置静态IP地址
# --------------------------------------------

def get_network_interface_list():
    """
    获取网络接口名称列表
    
    网络接口就是网卡的名字，比如 eth0, ens33 等
    这个函数会列出所有的网卡（除了本地回环 lo）
    
    返回值：
        网卡名称列表，比如 ['eth0', 'eth1']
    """
    try:
        # 读取 /sys/class/net 目录，这里面保存了所有网卡的信息
        all_interfaces = os.listdir('/sys/class/net')
        
        # 过滤掉 lo（本地回环接口），只保留真正的网卡
        real_interfaces = []
        for interface_name in all_interfaces:
            if interface_name != 'lo':  # lo 是本地回环，不是真正的网卡
                real_interfaces.append(interface_name)
        
        return real_interfaces
        
    except FileNotFoundError:
        print('[!] 错误：无法读取网络接口信息')
        return []


def get_command_output(command_list, work_directory=None):
    """
    Run a command and return stdout text, or an empty string on failure.
    """
    try:
        result = subprocess.run(
            command_list,
            check=True,
            cwd=work_directory,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True
        )
        return result.stdout.strip()
    except Exception:
        return ''


def get_existing_systemd_service(service_name_list):
    """
    从候选服务名里找出当前系统真实存在的那个。
    """
    if not check_command_exists('systemctl'):
        return None

    for service_name in service_name_list:
        result = subprocess.run(
            ['systemctl', 'list-unit-files', f'{service_name}.service', '--no-legend'],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True
        )
        if result.returncode == 0 and f'{service_name}.service' in result.stdout:
            return service_name

    return None


def start_and_enable_service(service_name_list):
    """
    启动并设置服务开机自启。
    """
    service_name = get_existing_systemd_service(service_name_list)
    if not service_name:
        return None

    print(f'[*] 启动 {service_name} 服务...')
    run_system_command(['systemctl', 'start', service_name])
    print(f'[*] 设置 {service_name} 开机自启...')
    run_system_command(['systemctl', 'enable', service_name])
    return service_name


def get_active_connection_name(interface_name):
    """
    Resolve the active NetworkManager connection name for an interface.
    """
    if not check_command_exists('nmcli'):
        return interface_name

    connection_name = get_command_output(
        ['nmcli', '-g', 'GENERAL.CONNECTION', 'device', 'show', interface_name]
    )
    if connection_name and connection_name != '--':
        return connection_name

    return interface_name


def get_current_network_defaults(interface_name):
    """
    Read current gateway and DNS values from NetworkManager for an interface.
    """
    network_defaults = {
        'gateway': '',
        'dns_servers': []
    }

    if not check_command_exists('nmcli'):
        return network_defaults

    gateway_output = get_command_output(
        ['nmcli', '-g', 'IP4.GATEWAY', 'device', 'show', interface_name]
    )
    if gateway_output:
        network_defaults['gateway'] = gateway_output.splitlines()[0].strip()

    dns_output = get_command_output(
        ['nmcli', '-g', 'IP4.DNS', 'device', 'show', interface_name]
    )
    if dns_output:
        dns_list = []
        for line in dns_output.splitlines():
            dns_server = line.strip()
            if dns_server and dns_server not in dns_list:
                dns_list.append(dns_server)
        network_defaults['dns_servers'] = dns_list

    return network_defaults


def get_recommended_dns_servers(detected_dns_list=None):
    """
    生成更通用的默认 DNS 列表。

    规则：
    1. 优先沿用当前检测到的 DNS
    2. 但不把 8.8.8.8 / 8.8.4.4 当默认首选，避免在部分国内网络里首次解析过慢
    3. 如果没有合适的当前 DNS，就回退到更通用的公共 DNS
    """
    if detected_dns_list is None:
        detected_dns_list = []

    preferred_dns = []
    deprioritized_dns = {'8.8.8.8', '8.8.4.4'}
    fallback_dns = ['223.5.5.5', '114.114.114.114']

    for dns_server in detected_dns_list:
        if dns_server and dns_server not in preferred_dns and dns_server not in deprioritized_dns:
            preferred_dns.append(dns_server)

    for dns_server in fallback_dns:
        if dns_server not in preferred_dns:
            preferred_dns.append(dns_server)

    for dns_server in detected_dns_list:
        if dns_server and dns_server not in preferred_dns:
            preferred_dns.append(dns_server)

    if len(preferred_dns) == 1:
        preferred_dns.append(fallback_dns[1] if preferred_dns[0] != fallback_dns[1] else fallback_dns[0])

    return preferred_dns[:2]


def is_vmware_virtual_machine():
    """
    Best-effort check for VMware guests.
    """
    if check_command_exists('systemd-detect-virt'):
        virt_type = get_command_output(['systemd-detect-virt'])
        if virt_type.lower() == 'vmware':
            return True

    dmi_file_list = [
        '/sys/class/dmi/id/sys_vendor',
        '/sys/class/dmi/id/product_name',
        '/sys/class/dmi/id/board_vendor'
    ]
    for dmi_file in dmi_file_list:
        try:
            with open(dmi_file, 'r', encoding='utf-8', errors='ignore') as file:
                if 'vmware' in file.read().strip().lower():
                    return True
        except Exception:
            continue

    return False


# --------------------------------------------
# 第四部分：网络配置功能
# 配置静态 IP，并做基础校验和应用
# --------------------------------------------

def choose_static_ip_interface():
    """
    让用户选择要配置静态 IP 的网卡。
    """
    interface_list = get_network_interface_list()
    if not interface_list:
        print('[!] 没有找到可用的网络接口')
        return None

    interface_options = [(f'网卡 {name}', name) for name in interface_list]
    chosen_interface = select_menu_option('请选择要配置的网卡', interface_options, '上/下选择网卡，回车确认')
    if chosen_interface is None:
        print('[*] 已取消选择网卡')
    return chosen_interface


def show_detected_network_defaults(detected_gateway, detected_dns_list, default_dns_list):
    """
    显示当前检测到的网关和 DNS 参考值。
    """
    if detected_gateway:
        print(f'[*] 当前检测到的网关：{detected_gateway}')

    if detected_dns_list:
        print(f'[*] 当前检测到的 DNS：{", ".join(detected_dns_list)}')
        if any(dns_server in ('8.8.8.8', '8.8.4.4') for dns_server in detected_dns_list):
            print(f'[*] 已自动调整推荐 DNS 为：{", ".join(default_dns_list)}')
            print('[*] 说明：8.8.8.8 在部分网络环境里首次解析可能较慢，所以不再作为默认首选')
    else:
        print(f'[*] 未检测到现有 DNS，默认推荐使用：{", ".join(default_dns_list)}')


def collect_static_ip_config(interface_name):
    """
    采集静态 IP 所需的参数。
    """
    current_network_defaults = get_current_network_defaults(interface_name)
    detected_gateway = current_network_defaults['gateway']
    detected_dns_list = current_network_defaults['dns_servers']
    recommended_dns_list = get_recommended_dns_servers(detected_dns_list)

    show_detected_network_defaults(detected_gateway, detected_dns_list, recommended_dns_list)

    default_dns1, default_dns2 = recommended_dns_list

    print('\n[*] 请输入网络参数')
    try:
        user_ip = input('  IP地址（例如 192.168.1.100）：').strip()
        ip_address(user_ip)

        user_netmask = input('  子网掩码（默认 255.255.255.0）：').strip()
        if not user_netmask:
            user_netmask = '255.255.255.0'
        else:
            ip_address(user_netmask)

        if detected_gateway:
            user_gateway = input(f'  网关（直接回车沿用 {detected_gateway}）：').strip()
            if not user_gateway:
                user_gateway = detected_gateway
        else:
            user_gateway = input('  网关（例如 192.168.1.1）：').strip()
        ip_address(user_gateway)

        user_dns1 = input(f'  首选 DNS（直接回车沿用 {default_dns1}）：').strip()
        if not user_dns1:
            user_dns1 = default_dns1
        else:
            ip_address(user_dns1)

        user_dns2 = input(f'  备用 DNS（直接回车沿用 {default_dns2}）：').strip()
        if not user_dns2:
            user_dns2 = default_dns2
        else:
            ip_address(user_dns2)

    except ValueError:
        print('[!] 错误：IP 地址格式不正确')
        return None

    netmask_cidr = ip_network(f'0.0.0.0/{user_netmask}', strict=False).prefixlen
    return {
        'interface': interface_name,
        'ip': user_ip,
        'netmask': user_netmask,
        'cidr': netmask_cidr,
        'gateway': user_gateway,
        'dns_servers': [user_dns1, user_dns2],
        'detected_gateway': detected_gateway,
        'detected_dns_list': detected_dns_list,
    }


def validate_static_ip_config(network_config):
    """
    校验静态 IP 参数是否合法。
    """
    target_subnet = ip_network(f"{network_config['ip']}/{network_config['cidr']}", strict=False)
    gateway_ip = ip_address(network_config['gateway'])

    if gateway_ip not in target_subnet:
        print(f"[!] 错误：网关 {network_config['gateway']} 不在网段 {target_subnet} 内")
        print('[!] 这种情况通常会导致内网能通、外网不通')
        return False

    if network_config['gateway'] == network_config['ip']:
        print('[!] 错误：网关不能和本机 IP 相同')
        return False

    return True


def confirm_static_ip_warnings(network_config):
    """
    对明显可疑的网络参数做二次提醒。
    """
    detected_gateway = network_config['detected_gateway']
    user_gateway = network_config['gateway']

    if detected_gateway and user_gateway != detected_gateway:
        print(f'[!] 提醒：当前检测到的网关是 {detected_gateway}，你输入的是 {user_gateway}')

    if is_vmware_virtual_machine() and user_gateway.endswith('.1'):
        print('[!] 提醒：VMware NAT 网络里，*.1 往往是宿主机地址，真正网关常见是 *.2')
        if detected_gateway and detected_gateway != user_gateway:
            print(f'[!] 当前检测到的网关参考值：{detected_gateway}')
        if not confirm_with_menu('仍然继续使用这个网关吗？', default=False):
            print('[*] 已取消配置，请重新执行并填写正确网关')
            return False

    return True


def show_static_ip_summary(network_config):
    """
    打印将要应用的静态 IP 配置。
    """
    print('\n即将应用的网络配置：')
    print('=' * 50)
    print(f"网卡：{network_config['interface']}")
    print(f"IP地址：{network_config['ip']}")
    print(f"子网掩码：{network_config['netmask']}")
    print(f"网关：{network_config['gateway']}")
    print(f"DNS1：{network_config['dns_servers'][0]}")
    print(f"DNS2：{network_config['dns_servers'][1]}")
    print('=' * 50)


def apply_redhat_static_ip_config(system_info, network_config):
    """
    在 RedHat 系列系统上应用静态 IP 配置。
    """
    print('\n[*] 正在为 RedHat 系列系统配置网络...')

    try:
        version_number = int(system_info['system_version'].split('.')[0])
    except Exception:
        version_number = 8

    if version_number >= 8 or system_info['system_type'] in ['rocky', 'almalinux']:
        print('[*] 使用 nmcli 配置网络')
        connection_name = get_active_connection_name(network_config['interface'])
        print(f'[*] 识别到的连接名：{connection_name}')

        command_steps = [
            (f"[*] 正在把 {network_config['interface']} 设置为静态 IP 模式...", ['nmcli', 'connection', 'modify', connection_name, 'ipv4.method', 'manual']),
            (f"[*] 正在设置 IP 地址：{network_config['ip']}/{network_config['cidr']}", ['nmcli', 'connection', 'modify', connection_name, 'ipv4.addresses', f"{network_config['ip']}/{network_config['cidr']}"]),
            (f"[*] 正在设置网关：{network_config['gateway']}", ['nmcli', 'connection', 'modify', connection_name, 'ipv4.gateway', network_config['gateway']]),
            (f"[*] 正在设置 DNS：{', '.join(network_config['dns_servers'])}", ['nmcli', 'connection', 'modify', connection_name, 'ipv4.dns', ' '.join(network_config['dns_servers'])]),
            ('[*] 正在设置开机自启...', ['nmcli', 'connection', 'modify', connection_name, 'connection.autoconnect', 'yes']),
            ('[*] 正在重新加载连接...', ['nmcli', 'connection', 'reload']),
        ]

        for message, command in command_steps:
            print(message)
            if not run_system_command(command):
                print('[!] 网络配置应用失败，请检查上面的错误信息')
                return

        print('[*] 正在激活连接...')
        if run_system_command(['nmcli', 'connection', 'up', connection_name]):
            print('[*] 网络配置已应用')
            print('[!] 如果你是通过 SSH 连接，网络重启时连接可能会短暂中断')
        else:
            print('[!] 激活网络连接失败')
        return

    print('[*] 使用传统 network-scripts 方式配置')
    config_text = f"""TYPE=Ethernet
BOOTPROTO=static
NAME={network_config['interface']}
DEVICE={network_config['interface']}
ONBOOT=yes
IPADDR={network_config['ip']}
NETMASK={network_config['netmask']}
GATEWAY={network_config['gateway']}
DNS1={network_config['dns_servers'][0]}
DNS2={network_config['dns_servers'][1]}
"""

    print('\n生成的配置如下：')
    print('=' * 50)
    print(config_text)
    print('=' * 50)

    if not confirm_with_menu('是否写入配置文件？'):
        print('[*] 已取消配置')
        return

    config_file_path = f"/etc/sysconfig/network-scripts/ifcfg-{network_config['interface']}"
    with open(config_file_path, 'w', encoding='utf-8') as config_file:
        config_file.write(config_text)

    print('[*] 正在重启网络服务...')
    if run_system_command(['systemctl', 'restart', 'network']):
        print('[*] 网络配置已应用')
    else:
        print('[!] 重启网络服务失败')


def apply_debian_static_ip_via_netplan(network_config):
    """
    用 netplan 配置 Debian/Ubuntu 静态 IP。
    """
    config_text = f"""network:
  version: 2
  renderer: networkd
  ethernets:
    {network_config['interface']}:
      dhcp4: no
      addresses: [{network_config['ip']}/{network_config['cidr']}]
      routes:
        - to: default
          via: {network_config['gateway']}
      nameservers:
        addresses: [{network_config['dns_servers'][0]}, {network_config['dns_servers'][1]}]
"""

    print('\n生成的 netplan 配置如下：')
    print('=' * 50)
    print(config_text)
    print('=' * 50)

    if not confirm_with_menu('是否写入配置文件？'):
        print('[*] 已取消配置')
        return

    config_file_path = f"/etc/netplan/01-{network_config['interface']}.yaml"
    with open(config_file_path, 'w', encoding='utf-8') as config_file:
        config_file.write(config_text)

    print('[*] 正在应用网络配置...')
    if run_system_command(['netplan', 'apply']):
        print('[*] 网络配置已应用')
    else:
        print('[!] 应用网络配置失败')


def apply_debian_static_ip_via_interfaces(network_config):
    """
    用 ifupdown 的 interfaces.d 配置 Debian 静态 IP。
    """
    config_text = f"""auto {network_config['interface']}
iface {network_config['interface']} inet static
    address {network_config['ip']}/{network_config['cidr']}
    gateway {network_config['gateway']}
    dns-nameservers {network_config['dns_servers'][0]} {network_config['dns_servers'][1]}
"""

    print('\n生成的 interfaces 配置如下：')
    print('=' * 50)
    print(config_text)
    print('=' * 50)

    if not confirm_with_menu('是否写入配置文件？'):
        print('[*] 已取消配置')
        return

    interfaces_dir = '/etc/network/interfaces.d'
    os.makedirs(interfaces_dir, exist_ok=True)
    config_file_path = f'{interfaces_dir}/{network_config["interface"]}'
    with open(config_file_path, 'w', encoding='utf-8') as config_file:
        config_file.write(config_text)

    print('[*] 正在重启 networking 服务...')
    if run_system_command(['systemctl', 'restart', 'networking']):
        print('[*] 网络配置已应用')
    else:
        print('[!] networking 服务重启失败，请确认系统正在使用 ifupdown')


def apply_debian_static_ip_via_nmcli(network_config):
    """
    用 NetworkManager 配置 Debian 静态 IP。
    """
    connection_name = get_active_connection_name(network_config['interface'])
    print(f'[*] 识别到的连接名：{connection_name}')

    command_steps = [
        (f"[*] 正在把 {network_config['interface']} 设置为静态 IP 模式...", ['nmcli', 'connection', 'modify', connection_name, 'ipv4.method', 'manual']),
        (f"[*] 正在设置 IP 地址：{network_config['ip']}/{network_config['cidr']}", ['nmcli', 'connection', 'modify', connection_name, 'ipv4.addresses', f"{network_config['ip']}/{network_config['cidr']}"]),
        (f"[*] 正在设置网关：{network_config['gateway']}", ['nmcli', 'connection', 'modify', connection_name, 'ipv4.gateway', network_config['gateway']]),
        (f"[*] 正在设置 DNS：{', '.join(network_config['dns_servers'])}", ['nmcli', 'connection', 'modify', connection_name, 'ipv4.dns', ' '.join(network_config['dns_servers'])]),
        ('[*] 正在设置开机自启...', ['nmcli', 'connection', 'modify', connection_name, 'connection.autoconnect', 'yes']),
        ('[*] 正在重新加载连接...', ['nmcli', 'connection', 'reload']),
    ]

    for message, command in command_steps:
        print(message)
        if not run_system_command(command):
            print('[!] 网络配置应用失败，请检查上面的错误信息')
            return

    print('[*] 正在激活连接...')
    if run_system_command(['nmcli', 'connection', 'up', connection_name]):
        print('[*] 网络配置已应用')
    else:
        print('[!] 激活网络连接失败')


def apply_debian_static_ip_config(network_config):
    """
    在 Debian 系列系统上应用静态 IP 配置。
    """
    print('\n[*] 正在为 Debian 系列系统配置网络...')

    if check_command_exists('netplan') or os.path.isdir('/etc/netplan'):
        print('[*] 检测到 netplan，使用 netplan 方式配置')
        apply_debian_static_ip_via_netplan(network_config)
        return

    if check_command_exists('nmcli'):
        print('[*] 检测到 NetworkManager，使用 nmcli 方式配置')
        apply_debian_static_ip_via_nmcli(network_config)
        return

    print('[*] 未检测到 netplan 或 NetworkManager，回退到 interfaces.d 方式配置')
    apply_debian_static_ip_via_interfaces(network_config)


def apply_static_ip_config(system_info, network_config):
    """
    按系统类型分发静态 IP 配置。
    """
    show_static_ip_summary(network_config)
    if not confirm_with_menu('是否应用配置？'):
        print('[*] 已取消配置')
        return

    system_family = system_info['system_family']
    if system_family == 'redhat':
        apply_redhat_static_ip_config(system_info, network_config)
    elif system_family == 'debian':
        apply_debian_static_ip_config(network_config)
    else:
        print('[!] 当前系统暂不支持自动配置静态 IP')


def config_static_ip(system_info):
    """
    配置静态 IP 地址。
    """
    chosen_interface = choose_static_ip_interface()
    if chosen_interface is None:
        return

    network_config = collect_static_ip_config(chosen_interface)
    if network_config is None:
        return

    if not validate_static_ip_config(network_config):
        return

    if not confirm_static_ip_warnings(network_config):
        return

    apply_static_ip_config(system_info, network_config)


# --------------------------------------------
# 第五部分：安全设置功能
# 关闭防火墙和 SELinux（生产环境请谨慎使用）
# --------------------------------------------

def disable_firewall_and_selinux(system_info):
    """
    关闭防火墙和 SELinux
    
    注意：这个操作会降低系统安全性！
    通常只在开发测试环境使用，生产环境请谨慎操作
    
    参数说明：
        system_info: 系统信息字典
    """
    system_family = system_info['system_family']
    
    if system_family == 'redhat':
        # RedHat 系列：关闭 firewalld 和 SELinux
        print('[*] 正在关闭 RedHat 系统的防火墙和 SELinux...')
        
        # 关闭 firewalld
        print('[*] 停止 firewalld 服务...')
        run_system_command(['systemctl', 'stop', 'firewalld'])
        
        print('[*] 禁用 firewalld 开机自启...')
        run_system_command(['systemctl', 'disable', 'firewalld'])
        
        # 临时关闭 SELinux
        print('[*] 临时关闭 SELinux...')
        run_system_command(['setenforce', '0'])
        
        # 永久关闭 SELinux（修改配置文件）
        print('[*] 永久禁用 SELinux...')
        run_system_command(['sed', '-i', 's/^SELINUX=enforcing/SELINUX=disabled/', '/etc/selinux/config'])
        
        print('[OK] firewalld 和 SELinux 已禁用')
        print('[!] 注意：SELinux 永久禁用需要重启系统才能生效')
    
    elif system_family == 'debian':
        # Debian 系列：关闭 ufw
        print('[*] 正在关闭 Debian 系统的防火墙...')

        if check_command_exists('ufw'):
            print('[*] 禁用 ufw 防火墙...')
            run_system_command(['ufw', 'disable'])
            print('[OK] ufw 防火墙已禁用')
        elif check_command_exists('systemctl') and get_existing_systemd_service(['firewalld']):
            print('[*] 检测到 firewalld，正在停止并禁用...')
            run_system_command(['systemctl', 'stop', 'firewalld'])
            run_system_command(['systemctl', 'disable', 'firewalld'])
            print('[OK] firewalld 已禁用')
        else:
            print('[*] 当前系统没有检测到受支持的防火墙管理工具，跳过自动处理')
    else:
        print('[!] 当前系统不支持自动关闭防火墙')


# --------------------------------------------
# 第五部分：软件源配置功能
# 更换国内镜像源，加快软件下载速度
# --------------------------------------------

def backup_file_if_exists(file_path, backup_path=None):
    """
    如果文件存在，就先备份一份。
    """
    if not os.path.exists(file_path):
        return None

    if backup_path is None:
        backup_path = f'{file_path}.backup'

    shutil.copy2(file_path, backup_path)
    return backup_path


def choose_repository_mirror(system_family, system_type):
    """
    选择要使用的软件源镜像。
    """
    if system_family != 'debian':
        return 'aliyun'

    title = '请选择软件源镜像'
    subtitle = '官方源更通用，尤其适合海外服务器'

    options = [('官方源（推荐）', 'official')]
    options.extend([
        ('阿里云', 'aliyun'),
        ('清华', 'tsinghua'),
        ('腾讯', 'tencent'),
    ])

    selected_mirror = select_menu_option(title, options, subtitle)
    return selected_mirror or 'official'


def write_text_file(file_path, content):
    """
    用 UTF-8 写文本文件。
    """
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(content)


def normalize_debian_codename(system_version, system_codename):
    """
    尽量拿到 Debian 的发行代号。
    """
    if system_codename and system_codename not in ['unknown', 'n/a', 'N/A']:
        return system_codename.strip().lower()

    codename_map = {
        '10': 'buster',
        '11': 'bullseye',
        '12': 'bookworm',
        '13': 'trixie',
    }
    version_major = str(system_version).split('.')[0]
    return codename_map.get(version_major, '')


def get_debian_mirror_endpoints(mirror_name):
    """
    返回 Debian 不同镜像对应的主仓库和安全仓库地址。
    """
    mirror_map = {
        'official': ('http://deb.debian.org/debian', 'http://security.debian.org/debian-security'),
        'aliyun': ('http://mirrors.aliyun.com/debian', 'http://mirrors.aliyun.com/debian-security'),
        'tsinghua': ('https://mirrors.tuna.tsinghua.edu.cn/debian', 'https://mirrors.tuna.tsinghua.edu.cn/debian-security'),
        'tencent': ('https://mirrors.cloud.tencent.com/debian', 'https://mirrors.cloud.tencent.com/debian-security'),
    }
    return mirror_map.get(mirror_name, mirror_map['official'])


def get_ubuntu_mirror_endpoints(mirror_name):
    """
    返回 Ubuntu 不同镜像对应的主仓库和安全仓库地址。
    """
    mirror_map = {
        'official': ('http://archive.ubuntu.com/ubuntu', 'http://security.ubuntu.com/ubuntu'),
        'aliyun': ('http://mirrors.aliyun.com/ubuntu', 'http://mirrors.aliyun.com/ubuntu'),
        'tsinghua': ('https://mirrors.tuna.tsinghua.edu.cn/ubuntu', 'https://mirrors.tuna.tsinghua.edu.cn/ubuntu'),
        'tencent': ('https://mirrors.cloud.tencent.com/ubuntu', 'https://mirrors.cloud.tencent.com/ubuntu'),
    }
    return mirror_map.get(mirror_name, mirror_map['official'])


def build_ubuntu_sources_content(system_codename, mirror_name):
    """
    生成 Ubuntu 软件源配置内容。
    """
    archive_url, security_url = get_ubuntu_mirror_endpoints(mirror_name)
    return f"""# Ubuntu 软件源
deb {archive_url} {system_codename} main restricted universe multiverse
deb {security_url} {system_codename}-security main restricted universe multiverse
deb {archive_url} {system_codename}-updates main restricted universe multiverse
deb {archive_url} {system_codename}-backports main restricted universe multiverse

# 源码仓库（可选）
# deb-src {archive_url} {system_codename} main restricted universe multiverse
"""


def build_debian_sources_content(system_version, system_codename, use_deb822, mirror_name):
    """
    生成 Debian 软件源配置内容。
    """
    debian_codename = normalize_debian_codename(system_version, system_codename)
    if not debian_codename:
        return None

    version_major = str(system_version).split('.')[0]
    components = ['main', 'contrib', 'non-free']
    if version_major.isdigit() and int(version_major) >= 12:
        components.append('non-free-firmware')
    components_text = ' '.join(components)
    archive_url, security_url = get_debian_mirror_endpoints(mirror_name)

    if use_deb822:
        keyring_file = '/usr/share/keyrings/debian-archive-keyring.gpg'
        common_fields = []
        if mirror_name == 'official' and os.path.exists(keyring_file):
            common_fields.append(f'Signed-By: {keyring_file}')

        main_stanza = [
            'Types: deb',
            f'URIs: {archive_url}',
            f'Suites: {debian_codename} {debian_codename}-updates',
            f'Components: {components_text}',
        ] + common_fields

        security_stanza = [
            'Types: deb',
            f'URIs: {security_url}',
            f'Suites: {debian_codename}-security',
            f'Components: {components_text}',
        ] + common_fields

        return '\n'.join(main_stanza) + '\n\n' + '\n'.join(security_stanza) + '\n'

    return f"""# Debian 软件源
deb {archive_url} {debian_codename} {components_text}
deb {archive_url} {debian_codename}-updates {components_text}
deb {security_url} {debian_codename}-security {components_text}
"""


def configure_debian_apt_sources(system_version, system_codename, mirror_name):
    """
    配置 Debian 的 APT 软件源，兼容传统 sources.list 和 Debian 12+ 的 deb822 格式。
    """
    sources_file = '/etc/apt/sources.list'
    deb822_file = '/etc/apt/sources.list.d/debian.sources'
    use_deb822 = os.path.exists(deb822_file)

    if str(system_version).split('.')[0].isdigit() and int(str(system_version).split('.')[0]) >= 12:
        use_deb822 = True

    backup_file = backup_file_if_exists(sources_file, '/etc/apt/sources.list.backup')
    if backup_file:
        print(f'[*] 备份原有软件源配置到: {backup_file}')

    deb822_backup = backup_file_if_exists(deb822_file, '/etc/apt/sources.list.d/debian.sources.backup')
    if deb822_backup:
        print(f'[*] 备份 deb822 软件源配置到: {deb822_backup}')

    new_sources_content = build_debian_sources_content(system_version, system_codename, use_deb822, mirror_name)
    if not new_sources_content:
        print('[!] 无法识别 Debian 发行代号，暂时不能自动生成软件源配置')
        return False

    if use_deb822:
        print('[*] 检测到 Debian 12+ 或 deb822 格式，使用 /etc/apt/sources.list.d/debian.sources')
        write_text_file(deb822_file, new_sources_content)
        if os.path.exists(sources_file):
            write_text_file(sources_file, '# 该文件由 ops_toolbox 保留，实际源配置请看 sources.list.d/debian.sources\n')
    else:
        print('[*] 使用传统 /etc/apt/sources.list 格式')
        write_text_file(sources_file, new_sources_content)
        if os.path.exists(deb822_file):
            write_text_file(deb822_file, '# 该文件由 ops_toolbox 暂时停用，避免与 sources.list 重复\n')

    return True


def change_software_repository(system_info):
    """
    更换软件源为国内镜像（阿里云镜像）
    
    这个功能可以让软件下载速度更快
    因为国内访问国外的软件源比较慢
    
    参数说明：
        system_info: 系统信息字典
    """
    system_type = system_info['system_type']
    system_version = system_info['system_version']
    system_name = system_info['system_name']
    system_codename = system_info['system_codename']
    system_family = system_info['system_family']
    package_manager = system_info['package_manager']
    mirror_name = choose_repository_mirror(system_family, system_type)
    
    if system_family == 'redhat':
        # RedHat 系列：CentOS、Rocky、Alma 等
        print('[*] 正在为 RedHat 系列系统更换软件源...')
        
        # 第一步：备份原有的软件源配置
        backup_directory = '/etc/yum.backup'
        print(f'[*] 创建备份目录: {backup_directory}')
        os.makedirs(backup_directory, exist_ok=True)
        
        # 把原来的配置文件移动到备份目录
        print('[*] 备份原有软件源配置...')
        # 使用 bash -c 来执行通配符命令
        run_system_command(['bash', '-c', f'mv /etc/yum.repos.d/*.repo {backup_directory}/ 2>/dev/null || true'])
        
        # 第二步：根据不同的系统下载对应的软件源配置
        if system_type == 'centos':
            # CentOS 系统
            if system_version.startswith('7'):
                print('[*] 配置 CentOS 7 软件源...')
                run_system_command(['wget', '-O', '/etc/yum.repos.d/CentOS-Base.repo', 
                                  'https://mirrors.aliyun.com/repo/Centos-7.repo'])
                run_system_command(['wget', '-O', '/etc/yum.repos.d/epel.repo', 
                                  'https://mirrors.aliyun.com/repo/epel-7.repo'])
            elif system_version.startswith('8'):
                print('[*] 配置 CentOS 8 软件源...')
                if 'Stream' in system_name:
                    run_system_command(['wget', '-O', '/etc/yum.repos.d/CentOS-Base.repo',
                                      'https://mirrors.aliyun.com/repo/centos-stream/8/CentOS-Stream-BaseOS.repo'])
                else:
                    run_system_command(['wget', '-O', '/etc/yum.repos.d/CentOS-Base.repo',
                                      'https://mirrors.aliyun.com/repo/Centos-8.repo'])
        
        elif system_type in ['rocky', 'almalinux']:
            # Rocky Linux 或 AlmaLinux
            print(f'[*] 配置 {system_type.title()} 软件源...')
            # 对于 Rocky/Alma，使用通用的 EL8/EL9 仓库
            version_major = system_version.split('.')[0]
            if version_major == '8':
                run_system_command(['wget', '-O', '/etc/yum.repos.d/Rocky-Base.repo',
                                  'https://mirrors.aliyun.com/repo/rocky/8/Rocky-BaseOS.repo'])
            elif version_major == '9':
                run_system_command(['wget', '-O', '/etc/yum.repos.d/Rocky-Base.repo',
                                  'https://mirrors.aliyun.com/repo/rocky/9/Rocky-BaseOS.repo'])
        
        # 第三步：清理并重建缓存
        print('[*] 清理软件包缓存...')
        run_system_command([package_manager, 'clean', 'all'])
        
        print('[*] 重建软件包缓存...')
        run_system_command([package_manager, 'makecache'])
        
        print('[OK] RedHat 系列系统软件源更换完成')
    
    elif system_family == 'debian':
        # Debian 系列：Ubuntu、Debian 等
        print('[*] 正在为 Debian 系列系统更换软件源...')
        print(f'[*] 已选择镜像：{mirror_name}')

        # 第二步：生成新的软件源配置
        if system_type == 'ubuntu':
            # Ubuntu 系统
            print(f'[*] 配置 Ubuntu {system_version} ({system_codename}) 软件源...')
            new_sources_content = build_ubuntu_sources_content(system_codename, mirror_name)
        elif system_type == 'debian':
            # Debian 系统
            print(f'[*] 配置 Debian {system_version} ({system_codename}) 软件源...')
            if not configure_debian_apt_sources(system_version, system_codename, mirror_name):
                return
            new_sources_content = None
        else:
            print('[!] 当前 Debian 系列系统暂不支持自动配置')
            return
        
        # 第三步：写入新的配置文件
        if system_type == 'ubuntu':
            sources_file = '/etc/apt/sources.list'
            backup_file = backup_file_if_exists(sources_file, '/etc/apt/sources.list.backup')
            if backup_file:
                print(f'[*] 备份原有软件源配置到: {backup_file}')
            write_text_file(sources_file, new_sources_content)
        
        # 第四步：更新软件包索引
        print('[*] 更新软件包索引...')
        if not run_system_command(['apt', 'update']):
            print('[!] 软件源文件已经写入，但 apt update 失败，请检查源配置或网络连通性')
            return
        
        print('[OK] Debian 系列系统软件源更换完成')
    else:
        print('[!] 当前系统不支持自动更换软件源')


# --------------------------------------------
# 第六部分：常用软件安装功能
# 安装开发和运维常用的工具
# --------------------------------------------

def install_common_tools(system_info):
    """
    安装常用的工具软件
    
    这些工具包括：
    - vim: 文本编辑器
    - wget: 文件下载工具
    - curl: 另一个文件下载和HTTP工具
    - net-tools: 网络工具（ifconfig等）
    - lrzsz: 文件上传下载工具（rz/sz命令）
    - bash-completion: bash 命令自动补全
    - git: 版本控制工具
    
    参数说明：
        system_info: 系统信息字典
    """
    # 定义要安装的常用工具列表
    common_tool_list = [
        'vim',              # 文本编辑器
        'wget',             # 下载工具
        'curl',             # HTTP工具
        'net-tools',        # 网络工具
        'lrzsz',            # 上传下载工具
        'bash-completion',  # 命令补全
        'git'               # 版本控制
    ]

    if system_info['system_family'] == 'debian':
        # Debian 下这些包经常会作为其他功能前置依赖用到
        common_tool_list.extend([
            'ca-certificates',
            'gnupg',
            'lsb-release'
        ])

    # 去重，保留原顺序
    common_tool_list = list(dict.fromkeys(common_tool_list))
    
    # 显示要安装的软件列表
    print('[*] 即将安装以下常用工具：')
    for tool_name in common_tool_list:
        print(f'    - {tool_name}')
    
    # 询问用户是否确认安装
    print()
    user_confirm = input('是否继续安装？(y/n): ')
    
    if user_confirm.lower() == 'y':
        # 创建包管理器对象
        pkg_manager = PackageManager(system_info)
        
        # 使用包管理器安装软件
        if pkg_manager.install_packages(common_tool_list):
            print('[OK] 常用工具安装完成')


# --------------------------------------------
# 第八部分：数据库安装功能
# 安装 MySQL 数据库
# --------------------------------------------

def install_mysql_database(system_info):
    """
    安装 MySQL 数据库
    
    MySQL 是最流行的开源关系型数据库
    
    参数说明：
        system_info: 系统信息字典
    """
    system_family = system_info['system_family']
    pkg_manager = PackageManager(system_info)
    
    print('[*] 正在安装 MySQL 数据库...')
    
    if system_family == 'redhat':
        # RedHat 系列：需要先配置 MySQL 仓库
        print('[*] 配置 MySQL 软件源（清华大学镜像）...')
        
        # 生成 MySQL 仓库配置文件
        mysql_repo_content = '''[mysql-connectors-community]
name=MySQL Connectors Community
baseurl=https://mirrors.tuna.tsinghua.edu.cn/mysql/yum/mysql-connectors-community-el7-$basearch/
enabled=1
gpgcheck=1
gpgkey=https://repo.mysql.com/RPM-GPG-KEY-mysql-2022

[mysql-tools-community]
name=MySQL Tools Community
baseurl=https://mirrors.tuna.tsinghua.edu.cn/mysql/yum/mysql-tools-community-el7-$basearch/
enabled=1
gpgcheck=1
gpgkey=https://repo.mysql.com/RPM-GPG-KEY-mysql-2022

[mysql-5.7-community]
name=MySQL 5.7 Community Server
baseurl=https://mirrors.tuna.tsinghua.edu.cn/mysql/yum/mysql-5.7-community-el7-$basearch/
enabled=1
gpgcheck=1
gpgkey=https://repo.mysql.com/RPM-GPG-KEY-mysql-2022
'''
        
        # 写入配置文件
        with open('/etc/yum.repos.d/mysql.repo', 'w') as repo_file:
            repo_file.write(mysql_repo_content)
        
        print('[*] MySQL 软件源配置完成')
        
        # 安装 MySQL
        if pkg_manager.install_packages(['mysql-community-server']):
            # 启动 MySQL 服务
            print('[*] 启动 MySQL 服务...')
            run_system_command(['systemctl', 'start', 'mysqld'])
            
            # 设置开机自启
            print('[*] 设置 MySQL 开机自启...')
            run_system_command(['systemctl', 'enable', 'mysqld'])
            
            print('[OK] MySQL 数据库安装完成')
            print('[!] 注意：MySQL 初始密码在日志文件中')
            print('[!] 请执行以下命令查看初始密码：')
            print('[!]   grep "temporary password" /var/log/mysqld.log')
        else:
            print('[!] MySQL 安装失败')
    
    elif system_family == 'debian':
        # Debian 系列：默认更适合安装 default-mysql-server
        print('[*] 在 Debian 系列系统上安装默认 MySQL 实现...')
        
        if pkg_manager.install_packages(['default-mysql-server']):
            service_name = start_and_enable_service(['mysql', 'mariadb'])
            if service_name:
                print(f'[OK] 数据库服务 {service_name} 已启动，并设置为开机自启')

            print('[OK] Debian 系列数据库安装完成')
            print('[!] 说明：Debian 默认通常安装的是 MariaDB（MySQL 兼容实现）')
            print('[!] 建议运行 mysql_secure_installation 命令进行安全配置')
        else:
            print('[!] Debian 系列数据库安装失败')
    else:
        print('[!] 当前系统不支持自动安装 MySQL')


# --------------------------------------------
# 第九部分：Docker 安装功能
# 使用官方脚本安装 Docker
# --------------------------------------------

def install_docker_engine(system_info=None):
    """
    安装 Docker 容器引擎
    
    Debian/Ubuntu 优先使用官方 APT 仓库安装；
    其他系统保留原来的便捷脚本方式。
    """
    if system_info is None:
        system_info = read_system_info()

    print('[*] 准备安装 Docker...')

    if system_info['system_family'] == 'debian':
        system_codename = system_info.get('system_codename') or ''
        if system_codename in ['unknown', 'n/a', 'N/A', '']:
            system_codename = normalize_debian_codename(system_info.get('system_version', ''), system_codename)

        if not system_codename:
            print('[!] 无法识别发行代号，暂时不能自动配置 Docker 官方仓库')
            return

        docker_repo_os = 'ubuntu' if system_info.get('system_type') == 'ubuntu' else 'debian'
        print(f'[*] 在 {docker_repo_os} 上使用 Docker 官方 APT 仓库安装...')
        if not run_system_command(['apt', 'update']):
            print('[!] apt update 失败，无法继续安装 Docker')
            return

        if not run_system_command(['apt', 'install', '-y', 'ca-certificates', 'curl', 'gnupg']):
            print('[!] Docker 依赖安装失败')
            return

        print('[*] 准备 Docker 仓库密钥目录...')
        os.makedirs('/etc/apt/keyrings', exist_ok=True)

        print('[*] 下载 Docker 官方 GPG 密钥...')
        if not run_system_command(['curl', '-fsSL', f'https://download.docker.com/linux/{docker_repo_os}/gpg', '-o', '/etc/apt/keyrings/docker.asc']):
            print('[!] Docker GPG 密钥下载失败')
            return

        run_system_command(['chmod', 'a+r', '/etc/apt/keyrings/docker.asc'])

        architecture = get_command_output(['dpkg', '--print-architecture']).strip() or 'amd64'
        docker_repo_content = (
            f'deb [arch={architecture} signed-by=/etc/apt/keyrings/docker.asc] '
            f'https://download.docker.com/linux/{docker_repo_os} {system_codename} stable\n'
        )
        write_text_file('/etc/apt/sources.list.d/docker.list', docker_repo_content)

        print('[*] 更新 Docker 软件包索引...')
        if not run_system_command(['apt', 'update']):
            print('[!] Docker 仓库已写入，但 apt update 失败')
            return

        docker_packages = [
            'docker-ce',
            'docker-ce-cli',
            'containerd.io',
            'docker-buildx-plugin',
            'docker-compose-plugin'
        ]
        if not run_system_command(['apt', 'install', '-y'] + docker_packages):
            print('[!] Docker 安装失败')
            return

        service_name = start_and_enable_service(['docker'])
        if service_name:
            print(f'[OK] {service_name} 服务已启动，并设置为开机自启')

        print('[OK] Docker 安装完成')
        return

    print('[*] 下载 Docker 安装脚本...')

    if not run_system_command(['wget', '-O', 'docker_install.sh', 'https://xuanyuan.cloud/docker.sh']):
        print('[!] Docker 安装脚本下载失败')
        return

    print('[*] 添加执行权限...')
    run_system_command(['chmod', '+x', 'docker_install.sh'])

    print('[*] 执行安装脚本...')
    run_system_command(['bash', 'docker_install.sh'])

    print('[OK] Docker 安装完成')


# --------------------------------------------
# 第十部分：菜单系统
# 提供上下键交互界面
# --------------------------------------------

def _display_width(text):
    """
    粗略计算字符串显示宽度，中文按 2 格处理。
    """
    return sum(2 if ord(char) > 127 else 1 for char in str(text))


def _truncate_display_text(text, max_width):
    """
    按显示宽度截断字符串，避免 curses 写出边界。
    """
    if max_width <= 0:
        return ''

    current_width = 0
    result = []
    for char in str(text):
        char_width = 2 if ord(char) > 127 else 1
        if current_width + char_width > max_width:
            break
        result.append(char)
        current_width += char_width
    return ''.join(result)


def _center_x(width, text):
    return max(0, (width - _display_width(text)) // 2)


def _run_menu_screen(stdscr, title, options, subtitle='上下键选择，回车确认，Esc 返回'):
    """
    curses 菜单界面。
    """
    curses.curs_set(0)
    stdscr.keypad(True)

    if curses.has_colors():
        curses.start_color()
        curses.use_default_colors()
        curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_CYAN)
        curses.init_pair(2, curses.COLOR_CYAN, -1)

    selected_index = 0

    while True:
        stdscr.clear()
        height, width = stdscr.getmaxyx()

        title_text = _truncate_display_text(title, max(0, width - 4))
        subtitle_text = _truncate_display_text(subtitle, max(0, width - 4))
        footer_text = '上/下选择   Enter 确认   Esc 返回'
        footer_text = _truncate_display_text(footer_text, max(0, width - 4))

        stdscr.addstr(1, _center_x(width, title_text), title_text, curses.A_BOLD)
        if curses.has_colors():
            stdscr.addstr(3, _center_x(width, subtitle_text), subtitle_text, curses.color_pair(2))
        else:
            stdscr.addstr(3, _center_x(width, subtitle_text), subtitle_text)

        if width > 4:
            stdscr.hline(4, 2, curses.ACS_HLINE, width - 4)

        top_row = 6
        max_label_width = max(0, width - 10)

        for idx, option in enumerate(options):
            label = option[0] if isinstance(option, tuple) else str(option)
            label = _truncate_display_text(label, max_label_width)
            row = top_row + idx
            if row >= height - 2:
                break

            text = '> ' + label if idx == selected_index else '  ' + label
            if idx == selected_index:
                style = curses.A_BOLD | (curses.color_pair(1) if curses.has_colors() else curses.A_REVERSE)
                stdscr.addstr(row, 4, text, style)
            else:
                stdscr.addstr(row, 4, text)

        if height >= 2:
            stdscr.addstr(height - 2, _center_x(width, footer_text), footer_text)

        stdscr.refresh()
        key = stdscr.getch()

        if key in (curses.KEY_UP, ord('k'), ord('K')):
            selected_index = (selected_index - 1) % len(options)
        elif key in (curses.KEY_DOWN, ord('j'), ord('J')):
            selected_index = (selected_index + 1) % len(options)
        elif key in (10, 13, curses.KEY_ENTER):
            selected_option = options[selected_index]
            if isinstance(selected_option, tuple):
                return selected_option[1]
            return selected_option
        elif key == 27:
            return None


def select_menu_option(title, options, subtitle='上下键选择，回车确认，Esc 返回'):
    """
    使用 curses 提供菜单选择；不支持时退回到数字输入。
    """
    try:
        return curses.wrapper(_run_menu_screen, title, options, subtitle)
    except curses.error:
        print(f'\n{title}')
        print(subtitle)
        for index, option in enumerate(options, start=1):
            label = option[0] if isinstance(option, tuple) else str(option)
            print(f'  {index}. {label}')

        fallback_choice = input('请输入编号: ').strip()
        if not fallback_choice.isdigit():
            return None

        fallback_index = int(fallback_choice) - 1
        if fallback_index < 0 or fallback_index >= len(options):
            return None

        selected_option = options[fallback_index]
        if isinstance(selected_option, tuple):
            return selected_option[1]
        return selected_option


def confirm_with_menu(prompt, default=True):
    """
    用菜单做是/否确认。
    """
    if default:
        options = [('是', True), ('否', False)]
    else:
        options = [('否', False), ('是', True)]

    result = select_menu_option(prompt, options, '上下键选择，回车确认')
    if result is None:
        return False
    return result


def clear_screen():
    """
    清屏。
    """
    os.system('cls' if os.name == 'nt' else 'clear')


def wait_for_enter(message='按回车继续...'):
    """
    等待用户确认后继续。
    """
    input(f'\n{message}')


def _run_optional_function(function_name, *args):
    """
    按函数名调用功能，没实现时给出友好提示。
    """
    function_object = globals().get(function_name)
    if callable(function_object):
        return function_object(*args)

    print(f'[!] 这个功能还没在脚本里实现：{function_name}')
    return None


# --------------------------------------------
# 第十一部分：系统巡检功能
# 检查系统运行状态
# --------------------------------------------

def run_system_check():
    """
    执行系统巡检，并可选发送微信通知。
    """
    print('[*] 准备执行系统巡检...')

    if not os.path.exists('check_system.sh'):
        print('[!] 当前目录没有找到 check_system.sh，暂时无法执行巡检')
        return

    push_to_wechat = confirm_with_menu('是否推送微信告警？', default=False)

    print('[*] 正在执行巡检脚本...')
    with open('check_system.log', 'w', encoding='utf-8') as log_file:
        subprocess.run(['bash', 'check_system.sh'], stdout=log_file, stderr=log_file)

    print('\n' + '=' * 60)
    print('巡检结果')
    print('=' * 60)
    subprocess.run(['cat', 'check_system.log'])
    print('=' * 60)

    if not push_to_wechat:
        return

    if not os.path.exists('wechat.py'):
        print('[!] 当前目录没有找到 wechat.py，无法发送微信通知')
        return

    print('[*] 正在发送微信通知...')
    with open('check_system.log', 'r', encoding='utf-8') as log_file:
        log_content = log_file.read()

    result = subprocess.run(
        ['python3', 'wechat.py', log_content],
        capture_output=True,
        text=True
    )

    if result.returncode == 0:
        print('[*] 微信通知发送成功')
    else:
        print('[!] 微信通知发送失败')
        if result.stderr:
            print(f'[!] 错误信息: {result.stderr}')


def run_initialization_menu(system_info):
    """
    系统初始化菜单。
    """
    actions = {
        'static_ip': lambda: config_static_ip(system_info),
        'firewall': lambda: disable_firewall_and_selinux(system_info),
        'repo': lambda: change_software_repository(system_info),
        'tools': lambda: install_common_tools(system_info),
    }

    options = [
        ('配置静态 IP', 'static_ip'),
        ('关闭防火墙和 SELinux', 'firewall'),
        ('更换软件源', 'repo'),
        ('安装常用工具', 'tools'),
        ('返回上一级', 'back'),
        ('退出程序', 'exit'),
    ]

    while True:
        clear_screen()
        choice = select_menu_option('系统初始化', options, '上下键选择功能，回车确认')

        if choice in (None, 'back'):
            return

        if choice == 'exit':
            print('[*] 已退出程序')
            sys.exit(0)

        clear_screen()
        actions[choice]()
        wait_for_enter()


def run_service_installation_menu(system_info):
    """
    常用服务安装菜单。
    """
    options = [
        ('安装 Apache（暂未实现）', 'apache'),
        ('安装 Nginx（暂未实现）', 'nginx'),
        ('安装 MySQL', 'mysql'),
        ('安装 Docker', 'docker'),
        ('返回上一级', 'back'),
        ('退出程序', 'exit'),
    ]

    while True:
        clear_screen()
        choice = select_menu_option('常用服务安装', options, '上下键选择功能，回车确认')

        if choice in (None, 'back'):
            return

        if choice == 'exit':
            print('[*] 已退出程序')
            sys.exit(0)

        clear_screen()
        if choice == 'apache':
            _run_optional_function('install_apache_web_server', system_info)
        elif choice == 'nginx':
            _run_optional_function('install_nginx_from_source', system_info)
        elif choice == 'mysql':
            install_mysql_database(system_info)
        elif choice == 'docker':
            install_docker_engine(system_info)

        wait_for_enter()


def main():
    """
    程序入口。
    """
    clear_screen()
    print('=' * 60)
    print('Linux 运维工具箱')
    print('=' * 60)
    print()

    check_if_linux_system()
    print()

    system_info = read_system_info()
    print()

    if not system_info.get('is_supported'):
        should_continue = confirm_with_menu('当前系统可能未完全适配，是否继续？', default=True)
        if not should_continue:
            print('[*] 已取消执行')
            return

    main_options = [
        ('系统初始化', 'init'),
        ('安装常用服务', 'service'),
        ('系统巡检', 'check'),
        ('退出程序', 'exit'),
    ]

    while True:
        clear_screen()
        choice = select_menu_option('Linux 运维工具箱', main_options, '上下键选择菜单，回车确认')

        if choice in (None, 'exit'):
            print('\n[*] 感谢使用 Linux 运维工具箱')
            break

        clear_screen()
        if choice == 'init':
            run_initialization_menu(system_info)
        elif choice == 'service':
            run_service_installation_menu(system_info)
        elif choice == 'check':
            run_system_check()
            wait_for_enter()


if __name__ == '__main__':
    main()
