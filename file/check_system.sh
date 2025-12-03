#!/bin/bash

# Linux 一键巡检脚本
# 原作者: liyb
# 由devnull个人修改
# 生成时间: $(date)

LOG_FILE="/opt/巡检报告_$(date +%F_%T).log"

# 初始化日志文件
echo "系统巡检报告" > $LOG_FILE
echo "生成时间: $(date)" >> $LOG_FILE

# 输出函数 - 仅输出到日志文件
log_only() {
    echo "$1" >> $LOG_FILE
}

# 输出函数 - 同时输出到屏幕和日志文件
log() {
    echo "$1" | tee -a $LOG_FILE
}

# 输出函数 - 仅输出到屏幕
print_only() {
    echo "$1"
}

# 收集所有数据并保存到日志文件
log_only ""
log_only ""
log_only "======================[1] 系统基本信息========================"

# 获取基本信息
HOSTNAME=$(hostname)
IP_ADDR=$(hostname -I | cut -d' ' -f1)
OS_INFO=$(cat /etc/os-release | grep PRETTY_NAME | cut -d= -f2 | tr -d '\"')
KERNEL_VER=$(uname -r)
UPTIME_START=$(uptime -s)
UPTIME_DURATION=$(uptime -p)
LOAD_AVG=$(uptime | awk -F'load average:' '{print $2}' | sed 's/^ *//')
CURRENT_TIME=$(date)

# 记录到日志
log_only "主机名: $HOSTNAME"
log_only "IP地址: $IP_ADDR"
log_only "操作系统: $OS_INFO"
log_only "内核版本: $KERNEL_VER"
log_only "启动时间: $UPTIME_START"
log_only "运行时长: $UPTIME_DURATION"
log_only "系统负载: $LOAD_AVG"
log_only "当前时间: $CURRENT_TIME"
log_only ""

log_only "======================[2] CPU 信息==========================:"

# 获取CPU信息
CPU_MODEL=$(lscpu | grep 'Model name' | awk -F: '{print $2}' | sed 's/^ *//')
CPU_LOGICAL=$(grep "processor" /proc/cpuinfo | sort -u | wc -l)
CPU_PHYSICAL=$(grep "physical id" /proc/cpuinfo | sort -u | wc -l)
CPU_USAGE=$(top -bn1 | grep '%Cpu' | awk '{print $2}')

# 记录到日志
log_only "CPU 型号: $CPU_MODEL"
log_only "逻辑CPU核数: $CPU_LOGICAL"
log_only "物理CPU核数: $CPU_PHYSICAL"
log_only "CPU 使用率: ${CPU_USAGE}%"
log_only ""

log_only "======================[3] 内存使用情况=========================="

# 获取内存信息
free -h >> $LOG_FILE
MEM_TOTAL=$(free -mh | awk "NR==2" | awk '{print $2}')
MEM_USED=$(free -mh | awk "NR==2" | awk '{print $3}')
MEM_FREE=$(free -mh | awk "NR==2" | awk '{print $7}')
MEM_USAGE_PCT=$(free | grep -i mem | awk '{print $3/$2*100}' | cut -c1-5)

# 记录到日志
log_only "总共内存: $MEM_TOTAL"
log_only "使用内存: $MEM_USED"
log_only "剩余内存: $MEM_FREE"
log_only "内存使用占比: ${MEM_USAGE_PCT}%"
log_only ""

log_only "======================[4] 磁盘使用情况=========================="

# 获取磁盘信息
df -hT >> $LOG_FILE

# 提取主要分区使用率
DISK_USAGE=$(df -h | grep -v "tmpfs\|devtmpfs\|loop" | awk 'NR>1 {print $6 " (" $5 ")"}')
log_only ""

log_only "======================[5] 服务状态检查=========================="

# 检查服务状态 - 使用ps命令过滤服务名的方式进行更准确的检查
log_only "检查特定服务状态 (Firewalld，SSH，Nginx，Apache，MySQL):"

# 初始化服务状态变量
RUNNING_SERVICES=""
STOPPED_SERVICES=""

# 服务名称与进程名称的映射
declare -A SERVICE_PROCESS_MAP
SERVICE_PROCESS_MAP=(  
    ["firewalld"]="firewalld"
    ["sshd"]="sshd"
    ["nginx"]="nginx"
    ["apache2"]="apache2|httpd"
    ["mysqld"]="mysqld|mariadb"
)

for service in "${!SERVICE_PROCESS_MAP[@]}"; do
    process_pattern=${SERVICE_PROCESS_MAP[$service]}
    # 使用ps命令检查进程是否存在
    if ps aux | grep -E "$process_pattern" | grep -v grep > /dev/null; then
        log_only "$service 服务状态: 正在运行"
        RUNNING_SERVICES="$RUNNING_SERVICES $service"
    else
        # 如果ps命令没有找到进程，尝试使用systemctl作为备用方法
        if systemctl is-active --quiet $service 2>/dev/null; then
            log_only "$service 服务状态: 正在运行 (通过systemctl检测)"
            RUNNING_SERVICES="$RUNNING_SERVICES $service"
        else
            log_only "$service 服务状态: 未运行"
            STOPPED_SERVICES="$STOPPED_SERVICES $service"
        fi
    fi
done
log_only ""

log_only "========================[6] 安全检查============================"
log_only "SSH 配置:"
grep -E "^#?PermitRootLogin|^#?PasswordAuthentication" /etc/ssh/sshd_config >> $LOG_FILE
log_only ""

log_only "系统用户:"
awk -F: '{if ($3 >= 1000) print $1}' /etc/passwd >> $LOG_FILE
log_only ""

log_only "========================[7] 登录记录============================"
log_only "当前登录用户:"
CURRENT_USERS=$(who)
echo "$CURRENT_USERS" >> $LOG_FILE

# 提取当前登录用户信息，格式为 "用户名 from IP地址"
CURRENT_USERS_FORMATTED=$(who | awk '{print $1 " from " $5}' | sed 's/[()]//g')
log_only ""

# 统计登录IP及次数
log_only "登录IP统计(近100条记录):"
# 使用正则表达式匹配IP地址格式(简化版，匹配形如xxx.xxx.xxx.xxx的格式)
LOGIN_IP_STATS=$(last -100 | grep -E '[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+' | awk '{for(i=1;i<=NF;i++) if($i ~ /^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+$/) print $i}' | sort | uniq -c | sort -nr)
echo "$LOGIN_IP_STATS" >> $LOG_FILE

# 提取前三个最常见的登录IP及次数
TOP_LOGIN_IPS=$(last -100 | grep -E '[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+' | awk '{for(i=1;i<=NF;i++) if($i ~ /^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+$/) print $i}' | sort | uniq -c | sort -nr | head -3 | awk '{print $2"("$1"次)"}' | tr '\n' ', ' | sed 's/,$//')
# 如果没有找到IP地址，设置一个默认值
if [ -z "$TOP_LOGIN_IPS" ]; then
    TOP_LOGIN_IPS="未检测到有效IP地址"
fi
log_only ""

log_only "最近登录记录:"
last -a | head -10 >> $LOG_FILE
log_only ""

log_only "========================[8] 系统日志检查============================"
log_only "登录失败日志:"
grep "Failed password" /var/log/auth.log | tail -10 >> $LOG_FILE 2>/dev/null || log_only "未检测到 auth.log 文件"
log_only ""

log_only "检查系统重启记录:"
REBOOT_RECORDS=$(last reboot | head -5)
echo "$REBOOT_RECORDS" >> $LOG_FILE

# 提取最近一次重启时间
LAST_REBOOT=$(last reboot | head -1 | awk '{print $5 " " $6 " " $7 " " $8}')
log_only ""

log_only "========================[9] 性能分析============================"
log_only "内存占用排行前5:"
MEM_TOP=$(ps aux --sort=-%mem | head -6)
echo "$MEM_TOP" >> $LOG_FILE

# 提取内存占用前3的进程
MEM_TOP3=$(ps aux --sort=-%mem | head -4 | tail -3 | awk '{print $11"("$2")"}' | tr '\n' ', ' | sed 's/,$//')
log_only ""

log_only "CPU 占用排行前5:"
CPU_TOP=$(ps aux --sort=-%cpu | head -6)
echo "$CPU_TOP" >> $LOG_FILE

# 提取CPU占用前3的进程
CPU_TOP3=$(ps aux --sort=-%cpu | head -4 | tail -3 | awk '{print $11"("$2")"}' | tr '\n' ', ' | sed 's/,$//')
log_only ""

log_only "=============================巡检完成============================"
log_only "巡检报告生成完成，保存路径: $LOG_FILE"

# 现在输出用户要求的格式
print_only ""
print_only "主机巡检: $HOSTNAME ($IP_ADDR)"
print_only "核心指标"
print_only "CPU : ${CPU_USAGE}%"
print_only "内存 : ${MEM_USAGE_PCT}% ($MEM_USED / $MEM_TOTAL)"
print_only "负载 : $LOAD_AVG"
print_only "磁盘 : $DISK_USAGE"
print_only "服务状态"

# 输出运行中的服务
if [ -n "$RUNNING_SERVICES" ]; then
    print_only "🟢 $(echo $RUNNING_SERVICES | sed 's/^ //') (运行中)"
fi

# 输出未运行的服务
if [ -n "$STOPPED_SERVICES" ]; then
    print_only "🔴 $(echo $STOPPED_SERVICES | sed 's/^ //') (未运行)"
fi

print_only "系统与安全"
print_only "当前在线 : $CURRENT_USERS_FORMATTED"
print_only "常用登录IP : $TOP_LOGIN_IPS"
print_only "最近重启 : $LAST_REBOOT"
print_only "资源占用Top3"
print_only "CPU : $CPU_TOP3"
print_only "内存 : $MEM_TOP3"

log "巡检报告生成完成，保存路径: $LOG_FILE"
log "请根据巡检内容检查系统状态！"
log ""