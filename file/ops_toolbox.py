from ipaddress import ip_address, ip_network
import os
import sys
import subprocess
import shutil

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
    print("[✓] 系统检查通过：这是一个Linux系统")
    
    # 第二步：检查用户权限（是否是root用户）
    print("[*] 正在检查用户权限...")
    current_user_id = os.geteuid()  # 获取当前用户的ID
    if current_user_id != 0:  # root用户的ID是0
        print('[!] 错误：当前用户不是root用户')
        print('[!] 请使用 sudo 或切换到 root 用户后再运行')
        sys.exit(1)  # 退出程序
    print("[✓] 权限检查通过：当前是root用户")


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
        print(f'[✓] 系统类型: {system_type}')
        print(f'[✓] 系统版本: {system_version}')
        print(f'[✓] 系统代号: {system_codename}')
        print(f'[✓] 系统名称: {system_name}')
        
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
        print('[✓] 识别为 Debian 系列系统，使用 apt 包管理器')
        return {
            'system_family': 'debian',
            'package_manager': 'apt',
            'is_supported': True
        }
        
    elif system_type_lower in redhat_family:
        # 这是 RedHat 家族
        # CentOS 8 / Rocky 8 / Alma 8 及以上使用 dnf
        # CentOS 7 及以下使用 yum
        print('[✓] 识别为 RedHat 系列系统')
        
        # 判断使用 yum 还是 dnf
        try:
            version_number = int(system_version.split('.')[0])
            if version_number >= 8:
                package_manager = 'dnf'
                print(f'[✓] 系统版本 >= 8，使用 dnf 包管理器')
            else:
                package_manager = 'yum'
                print(f'[✓] 系统版本 < 8，使用 yum 包管理器')
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
            run_system_command(['apt', 'update', '-y'])
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


def config_static_ip(system_info):
    """
    配置静态IP地址
    
    这个函数会：
    1. 询问用户要配置哪个网卡
    2. 询问IP地址、子网掩码、网关、DNS
    3. 根据系统类型生成配置文件
    4. 应用新的网络配置
    
    参数说明：
        system_info: 系统信息字典
    """
    # 第一步：获取所有网卡
    interface_list = get_network_interface_list()
    if not interface_list:
        print('[!] 没有找到可用的网络接口')
        return
    
    # 第二步：显示网卡，让用户选择
    print(f'[*] 检测到以下网络接口: {", ".join(interface_list)}')
    chosen_interface = input("请输入要配置的网络接口名称: ").strip()
    
    if chosen_interface not in interface_list:
        print('[!] 错误：输入的网络接口不存在')
        return
    
    # 第三步：获取IP配置信息
    print("\n[*] 请输入网络配置信息:")
    try:
        # 输入IP地址
        user_ip = input("  IP地址 (例如 192.168.1.100): ").strip()
        ip_address(user_ip)  # 验证IP地址格式是否正确
        
        # 输入子网掩码
        user_netmask = input("  子网掩码 (默认 255.255.255.0): ").strip()
        if not user_netmask:
            user_netmask = '255.255.255.0'
        else:
            ip_address(user_netmask)  # 验证格式
        
        # 输入网关
        user_gateway = input("  网关 (例如 192.168.1.1): ").strip()
        ip_address(user_gateway)  # 验证格式
        
        # 输入DNS（提供默认值）
        user_dns1 = input("  首选DNS (默认 8.8.8.8): ").strip()
        if not user_dns1:
            user_dns1 = '8.8.8.8'
        else:
            ip_address(user_dns1)  # 验证格式
        
        user_dns2 = input("  备用DNS (默认 114.114.114.114): ").strip()
        if not user_dns2:
            user_dns2 = '114.114.114.114'
        else:
            ip_address(user_dns2)  # 验证格式
            
    except ValueError:
        print('[!] 错误：IP地址格式不正确')
        return
    
    # 第四步：根据系统类型生成配置
    system_family = system_info['system_family']
    
    if system_family == 'redhat':
        # RedHat 系列：CentOS、Rocky、Alma 等
        print('\n[*] 正在为 RedHat 系列系统配置网络...')
        
        # 判断系统版本，决定配置方式
        try:
            version_number = int(system_info['system_version'].split('.')[0])
        except:
            version_number = 8  # 默认按新版本处理
        
        # CentOS 8+ / Rocky / Alma 使用 nmcli 方式
        if version_number >= 8 or system_info['system_type'] in ['rocky', 'almalinux']:
            print('[*] 检测到现代 RedHat 系列系统，使用 nmcli 配置网络')
            
            # 显示即将执行的配置
            print("\n即将执行的网络配置：")
            print("=" * 50)
            print(f"网卡: {chosen_interface}")
            print(f"IP地址: {user_ip}")
            print(f"子网掩码: {user_netmask}")
            print(f"网关: {user_gateway}")
            print(f"DNS1: {user_dns1}")
            print(f"DNS2: {user_dns2}")
            print("=" * 50)
            
            # 询问用户是否确认
            confirm = input('\n是否应用配置？(y/n): ')
            if confirm.lower() == 'y':
                # 把子网掩码转换成 CIDR 格式（比如 255.255.255.0 -> 24）
                netmask_cidr = ip_network(f'0.0.0.0/{user_netmask}', strict=False).prefixlen
                
                print('[*] 使用 nmcli 配置网络...')
                
                # 检查连接是否存在，如果不存在则创建
                # 先尝试修改现有连接
                connection_name = chosen_interface
                
                # 1. 设置为手动配置（关闭 DHCP）
                print(f'[*] 设置 {chosen_interface} 为静态IP模式...')
                run_system_command(['nmcli', 'connection', 'modify', connection_name, 
                                  'ipv4.method', 'manual'])
                
                # 2. 设置IP地址和子网掩码
                print(f'[*] 配置IP地址: {user_ip}/{netmask_cidr}')
                run_system_command(['nmcli', 'connection', 'modify', connection_name,
                                  'ipv4.addresses', f'{user_ip}/{netmask_cidr}'])
                
                # 3. 设置网关
                print(f'[*] 配置网关: {user_gateway}')
                run_system_command(['nmcli', 'connection', 'modify', connection_name,
                                  'ipv4.gateway', user_gateway])
                
                # 4. 设置DNS
                print(f'[*] 配置DNS: {user_dns1}, {user_dns2}')
                run_system_command(['nmcli', 'connection', 'modify', connection_name,
                                  'ipv4.dns', f'{user_dns1} {user_dns2}'])
                
                # 5. 设置开机自启
                run_system_command(['nmcli', 'connection', 'modify', connection_name,
                                  'connection.autoconnect', 'yes'])
                
                # 6. 重新加载配置并激活连接
                print('[*] 重新加载网络连接...')
                run_system_command(['nmcli', 'connection', 'reload'])
                
                print('[*] 激活网络连接...')
                if run_system_command(['nmcli', 'connection', 'up', connection_name]):
                    print('[✓] 网络配置已生效')
                    print('[!] 提示：如果通过SSH连接，连接可能会短暂中断')
                else:
                    print('[!] 网络连接激活失败，请检查配置')
            else:
                print('[*] 已取消配置')
        
        else:
            # CentOS 7 及更早版本使用传统的配置文件方式
            print('[*] 检测到 CentOS 7 或更早版本，使用传统配置文件方式')
            
            # 生成配置文件内容
            config_text = f"""TYPE=Ethernet
BOOTPROTO=static
NAME={chosen_interface}
DEVICE={chosen_interface}
ONBOOT=yes
IPADDR={user_ip}
NETMASK={user_netmask}
GATEWAY={user_gateway}
DNS1={user_dns1}
DNS2={user_dns2}
"""
            # 显示配置内容
            print("\n生成的配置内容：")
            print("=" * 50)
            print(config_text)
            print("=" * 50)
            
            # 询问用户是否确认
            confirm = input('\n是否写入配置文件？(y/n): ')
            if confirm.lower() == 'y':
                # 写入配置文件
                config_file_path = f'/etc/sysconfig/network-scripts/ifcfg-{chosen_interface}'
                with open(config_file_path, 'w') as config_file:
                    config_file.write(config_text)
                
                print('[✓] 配置文件已写入')
                print('[*] 正在重启网络服务...')
                
                # 重启网络服务使配置生效
                if run_system_command(['systemctl', 'restart', 'network']):
                    print('[✓] 网络配置已生效')
                else:
                    print('[!] network 服务重启失败')
            else:
                print('[*] 已取消配置')
    
    elif system_family == 'debian':
        # Debian 系列：Ubuntu、Debian 等
        # 使用 netplan 配置
        print('\n[*] 正在为 Debian 系列系统生成网络配置...')
        
        # 把子网掩码转换成 CIDR 格式（比如 255.255.255.0 -> 24）
        netmask_cidr = ip_network(f'0.0.0.0/{user_netmask}', strict=False).prefixlen
        
        # 生成 netplan 配置
        config_text = f"""network:
  version: 2
  renderer: networkd
  ethernets:
    {chosen_interface}:
      dhcp4: no
      addresses: [{user_ip}/{netmask_cidr}]
      routes:
        - to: default
          via: {user_gateway}
      nameservers:
        addresses: [{user_dns1}, {user_dns2}]
"""
        # 显示配置内容
        print("\n生成的配置内容：")
        print("=" * 50)
        print(config_text)
        print("=" * 50)
        
        # 询问用户是否确认
        confirm = input('\n是否写入配置文件？(y/n): ')
        if confirm.lower() == 'y':
            # 写入配置文件
            config_file_path = f'/etc/netplan/01-{chosen_interface}.yaml'
            with open(config_file_path, 'w') as config_file:
                config_file.write(config_text)
            
            print('[✓] 配置文件已写入')
            print('[*] 正在应用网络配置...')
            
            # 应用 netplan 配置
            if run_system_command(['netplan', 'apply']):
                print('[✓] 网络配置已生效')
            else:
                print('[!] 应用配置失败，请检查配置文件')
        else:
            print('[*] 已取消配置')
    else:
        print('[!] 当前系统不支持自动配置静态IP')


# --------------------------------------------
# 第四部分：安全设置功能
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
        
        print('[✓] firewalld 和 SELinux 已禁用')
        print('[!] 注意：SELinux 永久禁用需要重启系统才能生效')
    
    elif system_family == 'debian':
        # Debian 系列：关闭 ufw
        print('[*] 正在关闭 Debian 系统的防火墙...')
        
        print('[*] 禁用 ufw 防火墙...')
        run_system_command(['ufw', 'disable'])
        
        print('[✓] ufw 防火墙已禁用')
    else:
        print('[!] 当前系统不支持自动关闭防火墙')


# --------------------------------------------
# 第五部分：软件源配置功能
# 更换国内镜像源，加快软件下载速度
# --------------------------------------------

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
        
        print('[✓] RedHat 系列系统软件源更换完成')
    
    elif system_family == 'debian':
        # Debian 系列：Ubuntu、Debian 等
        print('[*] 正在为 Debian 系列系统更换软件源...')
        
        # 第一步：备份原有的软件源配置
        sources_file = '/etc/apt/sources.list'
        backup_file = '/etc/apt/sources.list.backup'
        
        print(f'[*] 备份原有软件源配置到: {backup_file}')
        shutil.copy(sources_file, backup_file)
        
        # 第二步：生成新的软件源配置
        if system_type == 'ubuntu':
            # Ubuntu 系统
            print(f'[*] 配置 Ubuntu {system_version} ({system_codename}) 软件源...')
            
            # 生成阿里云 Ubuntu 镜像源配置
            new_sources_content = f"""# 阿里云 Ubuntu 镜像源
deb http://mirrors.aliyun.com/ubuntu/ {system_codename} main restricted universe multiverse
deb http://mirrors.aliyun.com/ubuntu/ {system_codename}-security main restricted universe multiverse
deb http://mirrors.aliyun.com/ubuntu/ {system_codename}-updates main restricted universe multiverse
deb http://mirrors.aliyun.com/ubuntu/ {system_codename}-backports main restricted universe multiverse

# 源码仓库（可选）
# deb-src http://mirrors.aliyun.com/ubuntu/ {system_codename} main restricted universe multiverse
"""
        elif system_type == 'debian':
            # Debian 系统
            print(f'[*] 配置 Debian {system_version} ({system_codename}) 软件源...')
            new_sources_content = f"""# 阿里云 Debian 镜像源
deb http://mirrors.aliyun.com/debian/ {system_codename} main contrib non-free
deb http://mirrors.aliyun.com/debian-security {system_codename}/updates main contrib non-free
deb http://mirrors.aliyun.com/debian/ {system_codename}-updates main contrib non-free
"""
        else:
            print('[!] 当前 Debian 系列系统暂不支持自动配置')
            return
        
        # 第三步：写入新的配置文件
        with open(sources_file, 'w') as file:
            file.write(new_sources_content)
        
        # 第四步：更新软件包索引
        print('[*] 更新软件包索引...')
        run_system_command(['apt', 'update'])
        
        print('[✓] Debian 系列系统软件源更换完成')
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
            print('[✓] 常用工具安装完成')


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
            
            print('[✓] MySQL 数据库安装完成')
            print('[!] 注意：MySQL 初始密码在日志文件中')
            print('[!] 请执行以下命令查看初始密码：')
            print('[!]   grep "temporary password" /var/log/mysqld.log')
        else:
            print('[!] MySQL 安装失败')
    
    elif system_family == 'debian':
        # Debian 系列：直接安装
        print('[*] 在 Debian 系列系统上安装 MySQL...')
        
        if pkg_manager.install_packages(['mysql-server']):
            # 启动 MySQL 服务
            print('[*] 启动 MySQL 服务...')
            run_system_command(['systemctl', 'start', 'mysql'])
            
            # 设置开机自启
            print('[*] 设置 MySQL 开机自启...')
            run_system_command(['systemctl', 'enable', 'mysql'])
            
            print('[✓] MySQL 数据库安装完成')
            print('[!] 建议运行 mysql_secure_installation 命令进行安全配置')
        else:
            print('[!] MySQL 安装失败')
    else:
        print('[!] 当前系统不支持自动安装 MySQL')


# --------------------------------------------
# 第九部分：Docker 安装功能
# 使用官方脚本安装 Docker
# --------------------------------------------

def install_docker_engine():
    """
    安装 Docker 容器引擎
    
    使用便捷脚本快速安装 Docker
    """
    print('[*] 准备安装 Docker...')
    print('[*] 下载 Docker 安装脚本...')
    
    # 下载安装脚本
    if not run_system_command(['wget', '-O', 'docker_install.sh', 'https://xuanyuan.cloud/docker.sh']):
        print('[!] Docker 安装脚本下载失败')
        return
    
    # 添加执行权限
    print('[*] 添加执行权限...')
    run_system_command(['chmod', '+x', 'docker_install.sh'])
    
    # 执行安装脚本
    print('[*] 执行安装脚本...')
    run_system_command(['bash', 'docker_install.sh'])
    
    print('[✓] Docker 安装完成')


# --------------------------------------------
# 第十部分：系统巡检功能
# 检查系统运行状态
# --------------------------------------------

def run_system_check():
    """
    执行系统巡检
    
    这个功能会调用外部的巡检脚本
    并可以将结果推送到微信
    """
    print('[*] 准备执行系统巡检...')
    
    # 询问是否推送微信
    push_to_wechat = input('是否推送微信告警？(y/n): ')
    
    # 执行巡检脚本，将输出保存到日志文件
    print('[*] 正在执行巡检脚本...')
    with open('check_system.log', 'w') as log_file:
        subprocess.run(['bash', 'check_system.sh'], stdout=log_file, stderr=log_file)
    
    # 显示巡检结果
    print('\n' + '=' * 50)
    print('巡检结果：')
    print('=' * 50)
    subprocess.run(['cat', 'check_system.log'])
    print('=' * 50)
    
    # 如果用户选择推送微信
    if push_to_wechat.lower() == 'y':
        print('[*] 正在发送微信通知...')
        
        # 读取日志内容
        with open('check_system.log', 'r') as log_file:
            log_content = log_file.read()
        
        # 调用微信推送脚本
        result = subprocess.run(['python3', 'wechat.py', log_content],
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print('[✓] 微信通知发送成功')
        else:
            print('[!] 微信通知发送失败')
            if result.stderr:
                print(f'[!] 错误信息: {result.stderr}')



# --------------------------------------------
# 第十一部分：菜单系统
# 提供友好的交互界面
# --------------------------------------------

def clear_screen():
    """
    清屏函数
    
    让界面看起来更整洁
    """
    subprocess.run(['clear'])


def show_initialization_menu():
    """
    显示系统初始化菜单
    
    这个菜单包含系统初始化的各项功能
    """
    menu_text = """
╔═══════════════════════════════════════╗
║     Linux 服务器基础初始化菜单        ║
╠═══════════════════════════════════════╣
║  1. 配置静态IP地址                    ║
║  2. 关闭防火墙和 SELinux              ║
║  3. 更换软件源（国内镜像）            ║
║  4. 安装常用工具                      ║
║  5. 返回上一级菜单                    ║
║  0. 退出程序                          ║
╚═══════════════════════════════════════╝
"""
    print(menu_text)


def run_initialization_menu(system_info):
    """
    运行系统初始化菜单
    
    参数说明：
        system_info: 系统信息字典
    """
    while True:
        clear_screen()
        show_initialization_menu()
        
        # 获取用户选择
        user_choice = input("请输入您的选择: ").strip()
        
        # 根据用户选择执行对应功能
        if user_choice == '1':
            # 配置静态IP
            config_static_ip(system_info)
            
        elif user_choice == '2':
            # 关闭防火墙
            disable_firewall_and_selinux(system_info)
            
        elif user_choice == '3':
            # 更换软件源
            change_software_repository(system_info)
            
        elif user_choice == '4':
            # 安装常用工具
            install_common_tools(system_info)
            
        elif user_choice == '5':
            # 返回上一级菜单
            break
            
        elif user_choice == '0':
            # 退出程序
            print('[*] 退出程序')
            sys.exit(0)
            
        else:
            # 无效选择
            print('[!] 无效选择，请重新输入')
        
        # 等待用户按键继续
        input('\n按回车键继续...')


def show_service_installation_menu():
    """
    显示服务安装菜单
    
    这个菜单包含常用服务的安装功能
    """
    menu_text = """
╔═══════════════════════════════════════╗
║     常用服务安装菜单                  ║
╠═══════════════════════════════════════╣
║  1. 安装 Apache Web 服务器            ║
║  2. 安装 Nginx（源码编译）            ║
║  3. 安装 MySQL 数据库                 ║
║  4. 安装 Docker 容器引擎              ║
║  5. 返回上一级菜单                    ║
║  0. 退出程序                          ║
╚═══════════════════════════════════════╝
"""
    print(menu_text)


def run_service_installation_menu(system_info):
    """
    运行服务安装菜单
    
    参数说明：
        system_info: 系统信息字典
    """
    while True:
        clear_screen()
        show_service_installation_menu()
        
        # 获取用户选择
        user_choice = input("请输入您的选择: ").strip()
        
        # 根据用户选择执行对应功能
        if user_choice == '1':
            # 安装 Apache
            install_apache_web_server(system_info)
            
        elif user_choice == '2':
            # 安装 Nginx
            install_nginx_from_source(system_info)
            
        elif user_choice == '3':
            # 安装 MySQL
            install_mysql_database(system_info)
            
        elif user_choice == '4':
            # 安装 Docker
            install_docker_engine()
            
        elif user_choice == '5':
            # 返回上一级菜单
            break
            
        elif user_choice == '0':
            # 退出程序
            print('[*] 退出程序')
            sys.exit(0)
            
        else:
            # 无效选择
            print('[!] 无效选择，请重新输入')
        
        # 等待用户按键继续
        input('\n按回车键继续...')


def show_main_menu():
    """
    显示主菜单
    
    这是程序的入口菜单
    """
    menu_text = """
╔═══════════════════════════════════════╗
║      Linux 运维工具箱 - 主菜单        ║
╠═══════════════════════════════════════╣
║  1. 系统初始化                        ║
║  2. 安装常用服务                      ║
║  3. 系统巡检                          ║
║  0. 退出程序                          ║
╚═══════════════════════════════════════╝
"""
    print(menu_text)


# --------------------------------------------
# 第十二部分：主程序入口
# 程序从这里开始运行
# --------------------------------------------

def main():
    """
    主程序入口函数
    
    这是程序开始运行的地方
    它会：
    1. 检查系统和权限
    2. 读取系统信息
    3. 显示主菜单
    4. 根据用户选择执行相应功能
    """
    # 第一步：显示欢迎信息
    print('=' * 50)
    print('       Linux 运维工具箱')
    print('=' * 50)
    print()
    
    # 第二步：检查系统和权限
    check_if_linux_system()
    print()
    
    # 第三步：读取系统信息
    system_info = read_system_info()
    print()
    
    # 检查系统是否被支持
    if not system_info['is_supported']:
        print('[!] 警告：当前系统可能不被完全支持')
        confirm = input('[?] 是否继续？(y/n): ')
        if confirm.lower() != 'y':
            print('[*] 退出程序')
            sys.exit(0)
    
    # 第四步：进入主菜单循环
    while True:
        clear_screen()
        show_main_menu()
        
        # 获取用户选择
        user_choice = input("请输入您的选择: ").strip()
        
        # 根据用户选择执行对应功能
        if user_choice == '1':
            # 系统初始化
            run_initialization_menu(system_info)
            
        elif user_choice == '2':
            # 安装常用服务
            run_service_installation_menu(system_info)
            
        elif user_choice == '3':
            # 系统巡检
            run_system_check()
            
        elif user_choice == '0':
            # 退出程序
            print()
            print('[*] 感谢使用 Linux 运维工具箱！')
            print('[*] 再见！')
            break
            
        else:
            # 无效选择
            print('[!] 无效选择，请重新输入')
        
        # 等待用户按键继续
        input('\n按回车键继续...')


# 程序入口
# 如果这个文件是直接运行的（不是被导入的），就执行 main 函数
if __name__ == '__main__':
    main()