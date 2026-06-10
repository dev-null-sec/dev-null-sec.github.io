import{bQ as a,aL as n,u as p,G as i}from"./chunks/framework.D06dwy5q.js";const o=JSON.parse('{"title":"Keepalived","description":"","frontmatter":{},"headers":[],"relativePath":"08.负载均衡与高可用/04-Keepalived.md","filePath":"08.负载均衡与高可用/04-Keepalived.md","lastUpdated":null}'),e={name:"08.负载均衡与高可用/04-Keepalived.md"};function t(l,s,h,d,c,r){return n(),p("div",null,[...s[0]||(s[0]=[i(`<h1 id="keepalived" tabindex="-1">Keepalived <a class="header-anchor" href="#keepalived" aria-label="Permalink to &quot;Keepalived&quot;">​</a></h1><p>Keepalived 常用于通过 VRRP 实现 VIP 漂移，配置重点在 <code>vrrp_instance</code>、优先级、抢占、健康检查脚本、VIP、通知和与 LVS/HAProxy/Nginx 的配合。</p><h2 id="一、keepalived-解决什么" tabindex="-1">一、Keepalived 解决什么 <a class="header-anchor" href="#一、keepalived-解决什么" aria-label="Permalink to &quot;一、Keepalived 解决什么&quot;">​</a></h2><p>负载均衡实例本身也可能故障。Keepalived 常用来让一个 VIP 在两台或多台入口机器之间漂移。</p><div class="mermaid-diagram" data-mermaid-code="flowchart%20LR%0A%20%20%20%20client%5B%22%E5%AE%A2%E6%88%B7%E7%AB%AF%22%5D%20--%3E%20vip%5B%22VIP%22%5D%0A%20%20%20%20vip%20--%3E%20lb01%5B%22lb01%20%E4%B8%BB%E5%85%A5%E5%8F%A3%22%5D%0A%20%20%20%20vip%20-.%20%22%E5%A4%87%E7%94%A8%22%20.-%3E%20lb02%5B%22lb02%20%E5%A4%87%E7%94%A8%E5%85%A5%E5%8F%A3%22%5D%0A"></div><p>当主入口机器故障，备用入口接管 VIP：</p><div class="mermaid-diagram" data-mermaid-code="flowchart%20LR%0A%20%20%20%20client%5B%22%E5%AE%A2%E6%88%B7%E7%AB%AF%22%5D%20--%3E%20vip%5B%22VIP%22%5D%0A%20%20%20%20vip%20--%3E%20lb02%5B%22lb02%20%E6%8E%A5%E7%AE%A1%E5%85%A5%E5%8F%A3%22%5D%0A"></div><p>Keepalived 使用 VRRP 协议做主备选举：多台机器约定一个虚拟路由器身份，当前 master 持有 VIP，backup 监听 master 的通告。master 不再通告时，backup 根据优先级接管。</p><h2 id="二、几个核心概念" tabindex="-1">二、几个核心概念 <a class="header-anchor" href="#二、几个核心概念" aria-label="Permalink to &quot;二、几个核心概念&quot;">​</a></h2><table tabindex="0"><thead><tr><th>概念</th><th>含义</th></tr></thead><tbody><tr><td>VRRP</td><td>虚拟路由冗余协议</td></tr><tr><td>VIP</td><td>漂移的虚拟 IP</td></tr><tr><td>MASTER</td><td>当前持有 VIP 的节点</td></tr><tr><td>BACKUP</td><td>等待接管的节点</td></tr><tr><td>priority</td><td>优先级，越大越容易成为 MASTER</td></tr><tr><td>advert_int</td><td>VRRP 通告间隔</td></tr><tr><td>virtual_router_id</td><td>同一组 VRRP 实例的标识</td></tr><tr><td>track_script</td><td>根据脚本结果调整权重或触发切换</td></tr></tbody></table><p>Keepalived 的角色是”入口地址接管工具”，不是完整负载均衡。真正分发流量的是 LVS、HAProxy、Nginx 或云 LB，Keepalived 负责让 VIP 落在健康的入口机器上。</p><h2 id="三、安装" tabindex="-1">三、安装 <a class="header-anchor" href="#三、安装" aria-label="Permalink to &quot;三、安装&quot;">​</a></h2><p>RHEL / Rocky / CentOS：</p><div class="language-bash vp-adaptive-theme"><button title="Copy Code" class="copy"></button><span class="lang">bash</span><pre class="shiki shiki-themes github-light github-dark vp-code" tabindex="0"><code><span class="line"><span style="--shiki-light:#6F42C1;--shiki-dark:#B392F0;">yum</span><span style="--shiki-light:#032F62;--shiki-dark:#9ECBFF;"> install</span><span style="--shiki-light:#005CC5;--shiki-dark:#79B8FF;"> -y</span><span style="--shiki-light:#032F62;--shiki-dark:#9ECBFF;"> keepalived</span></span>
<span class="line"><span style="--shiki-light:#6F42C1;--shiki-dark:#B392F0;">systemctl</span><span style="--shiki-light:#032F62;--shiki-dark:#9ECBFF;"> enable</span><span style="--shiki-light:#005CC5;--shiki-dark:#79B8FF;"> --now</span><span style="--shiki-light:#032F62;--shiki-dark:#9ECBFF;"> keepalived</span></span>
<span class="line"><span style="--shiki-light:#6F42C1;--shiki-dark:#B392F0;">keepalived</span><span style="--shiki-light:#005CC5;--shiki-dark:#79B8FF;"> -v</span></span></code></pre></div><p>Debian / Ubuntu：</p><div class="language-bash vp-adaptive-theme"><button title="Copy Code" class="copy"></button><span class="lang">bash</span><pre class="shiki shiki-themes github-light github-dark vp-code" tabindex="0"><code><span class="line"><span style="--shiki-light:#6F42C1;--shiki-dark:#B392F0;">apt</span><span style="--shiki-light:#032F62;--shiki-dark:#9ECBFF;"> update</span></span>
<span class="line"><span style="--shiki-light:#6F42C1;--shiki-dark:#B392F0;">apt</span><span style="--shiki-light:#032F62;--shiki-dark:#9ECBFF;"> install</span><span style="--shiki-light:#005CC5;--shiki-dark:#79B8FF;"> -y</span><span style="--shiki-light:#032F62;--shiki-dark:#9ECBFF;"> keepalived</span></span>
<span class="line"><span style="--shiki-light:#6F42C1;--shiki-dark:#B392F0;">systemctl</span><span style="--shiki-light:#032F62;--shiki-dark:#9ECBFF;"> enable</span><span style="--shiki-light:#005CC5;--shiki-dark:#79B8FF;"> --now</span><span style="--shiki-light:#032F62;--shiki-dark:#9ECBFF;"> keepalived</span></span>
<span class="line"><span style="--shiki-light:#6F42C1;--shiki-dark:#B392F0;">keepalived</span><span style="--shiki-light:#005CC5;--shiki-dark:#79B8FF;"> -v</span></span></code></pre></div><p>配置文件：</p><div class="language-text vp-adaptive-theme"><button title="Copy Code" class="copy"></button><span class="lang">text</span><pre class="shiki shiki-themes github-light github-dark vp-code" tabindex="0"><code><span class="line"><span>/etc/keepalived/keepalived.conf</span></span></code></pre></div><p>检查服务：</p><div class="language-bash vp-adaptive-theme"><button title="Copy Code" class="copy"></button><span class="lang">bash</span><pre class="shiki shiki-themes github-light github-dark vp-code" tabindex="0"><code><span class="line"><span style="--shiki-light:#6F42C1;--shiki-dark:#B392F0;">systemctl</span><span style="--shiki-light:#032F62;--shiki-dark:#9ECBFF;"> status</span><span style="--shiki-light:#032F62;--shiki-dark:#9ECBFF;"> keepalived</span><span style="--shiki-light:#005CC5;--shiki-dark:#79B8FF;"> --no-pager</span></span>
<span class="line"><span style="--shiki-light:#6F42C1;--shiki-dark:#B392F0;">journalctl</span><span style="--shiki-light:#005CC5;--shiki-dark:#79B8FF;"> -u</span><span style="--shiki-light:#032F62;--shiki-dark:#9ECBFF;"> keepalived</span><span style="--shiki-light:#005CC5;--shiki-dark:#79B8FF;"> -n</span><span style="--shiki-light:#005CC5;--shiki-dark:#79B8FF;"> 100</span><span style="--shiki-light:#005CC5;--shiki-dark:#79B8FF;"> --no-pager</span></span></code></pre></div><h2 id="四、基础主备配置" tabindex="-1">四、基础主备配置 <a class="header-anchor" href="#四、基础主备配置" aria-label="Permalink to &quot;四、基础主备配置&quot;">​</a></h2><p>示例环境：</p><table tabindex="0"><thead><tr><th>角色</th><th>地址</th></tr></thead><tbody><tr><td>lb01</td><td><code>192.168.10.11</code></td></tr><tr><td>lb02</td><td><code>192.168.10.12</code></td></tr><tr><td>VIP</td><td><code>192.168.10.100</code></td></tr><tr><td>网卡</td><td><code>eth0</code></td></tr></tbody></table><p>lb01 配置：</p><div class="language-conf vp-adaptive-theme"><button title="Copy Code" class="copy"></button><span class="lang">conf</span><pre class="shiki shiki-themes github-light github-dark vp-code" tabindex="0"><code><span class="line"><span># /etc/keepalived/keepalived.conf</span></span>
<span class="line"><span>vrrp_instance VI_1 {</span></span>
<span class="line"><span>    state MASTER</span></span>
<span class="line"><span>    interface eth0</span></span>
<span class="line"><span>    virtual_router_id 51</span></span>
<span class="line"><span>    priority 120</span></span>
<span class="line"><span>    advert_int 1</span></span>
<span class="line"><span></span></span>
<span class="line"><span>    authentication {</span></span>
<span class="line"><span>        auth_type PASS</span></span>
<span class="line"><span>        auth_pass 12345678</span></span>
<span class="line"><span>    }</span></span>
<span class="line"><span></span></span>
<span class="line"><span>    virtual_ipaddress {</span></span>
<span class="line"><span>        192.168.10.100/24 dev eth0</span></span>
<span class="line"><span>    }</span></span>
<span class="line"><span>}</span></span></code></pre></div><p>lb02 配置：</p><div class="language-conf vp-adaptive-theme"><button title="Copy Code" class="copy"></button><span class="lang">conf</span><pre class="shiki shiki-themes github-light github-dark vp-code" tabindex="0"><code><span class="line"><span>vrrp_instance VI_1 {</span></span>
<span class="line"><span>    state BACKUP</span></span>
<span class="line"><span>    interface eth0</span></span>
<span class="line"><span>    virtual_router_id 51</span></span>
<span class="line"><span>    priority 100</span></span>
<span class="line"><span>    advert_int 1</span></span>
<span class="line"><span></span></span>
<span class="line"><span>    authentication {</span></span>
<span class="line"><span>        auth_type PASS</span></span>
<span class="line"><span>        auth_pass 12345678</span></span>
<span class="line"><span>    }</span></span>
<span class="line"><span></span></span>
<span class="line"><span>    virtual_ipaddress {</span></span>
<span class="line"><span>        192.168.10.100/24 dev eth0</span></span>
<span class="line"><span>    }</span></span>
<span class="line"><span>}</span></span></code></pre></div><p>关键点：</p><table tabindex="0"><thead><tr><th>配置</th><th>说明</th></tr></thead><tbody><tr><td><code>virtual_router_id</code></td><td>同一组主备保持一致，不同组错开</td></tr><tr><td><code>priority</code></td><td>优先级越高越容易成为 MASTER</td></tr><tr><td><code>interface</code></td><td>VIP 绑定在哪张网卡</td></tr><tr><td><code>virtual_ipaddress</code></td><td>要漂移的 VIP</td></tr></tbody></table><p>启动：</p><div class="language-bash vp-adaptive-theme"><button title="Copy Code" class="copy"></button><span class="lang">bash</span><pre class="shiki shiki-themes github-light github-dark vp-code" tabindex="0"><code><span class="line"><span style="--shiki-light:#6F42C1;--shiki-dark:#B392F0;">systemctl</span><span style="--shiki-light:#032F62;--shiki-dark:#9ECBFF;"> restart</span><span style="--shiki-light:#032F62;--shiki-dark:#9ECBFF;"> keepalived</span></span>
<span class="line"><span style="--shiki-light:#6F42C1;--shiki-dark:#B392F0;">ip</span><span style="--shiki-light:#032F62;--shiki-dark:#9ECBFF;"> addr</span><span style="--shiki-light:#032F62;--shiki-dark:#9ECBFF;"> show</span><span style="--shiki-light:#032F62;--shiki-dark:#9ECBFF;"> dev</span><span style="--shiki-light:#032F62;--shiki-dark:#9ECBFF;"> eth0</span><span style="--shiki-light:#D73A49;--shiki-dark:#F97583;"> |</span><span style="--shiki-light:#6F42C1;--shiki-dark:#B392F0;"> grep</span><span style="--shiki-light:#005CC5;--shiki-dark:#79B8FF;"> 192.168.10.100</span></span></code></pre></div><h2 id="五、组播和单播" tabindex="-1">五、组播和单播 <a class="header-anchor" href="#五、组播和单播" aria-label="Permalink to &quot;五、组播和单播&quot;">​</a></h2><p>VRRP 默认常见形态是组播通告，地址一般是 <code>224.0.0.18</code>，协议号是 <code>112</code>。同一二层网络里，backup 能收到 master 的 VRRP 通告，就不会抢 VIP。</p><p>虚拟化平台、云 VPC、跨交换机安全策略里，组播可能被限制。现象通常是两台机器都认为自己收不到对方通告，于是都进入 MASTER，VIP 同时出现在两台机器上。这类环境更适合配置 unicast peer。</p><p>lb01：</p><div class="language-conf vp-adaptive-theme"><button title="Copy Code" class="copy"></button><span class="lang">conf</span><pre class="shiki shiki-themes github-light github-dark vp-code" tabindex="0"><code><span class="line"><span>vrrp_instance VI_1 {</span></span>
<span class="line"><span>    state MASTER</span></span>
<span class="line"><span>    interface eth0</span></span>
<span class="line"><span>    virtual_router_id 51</span></span>
<span class="line"><span>    priority 120</span></span>
<span class="line"><span>    advert_int 1</span></span>
<span class="line"><span></span></span>
<span class="line"><span>    unicast_src_ip 192.168.10.11</span></span>
<span class="line"><span>    unicast_peer {</span></span>
<span class="line"><span>        192.168.10.12</span></span>
<span class="line"><span>    }</span></span>
<span class="line"><span></span></span>
<span class="line"><span>    virtual_ipaddress {</span></span>
<span class="line"><span>        192.168.10.100/24 dev eth0</span></span>
<span class="line"><span>    }</span></span>
<span class="line"><span>}</span></span></code></pre></div><p>lb02：</p><div class="language-conf vp-adaptive-theme"><button title="Copy Code" class="copy"></button><span class="lang">conf</span><pre class="shiki shiki-themes github-light github-dark vp-code" tabindex="0"><code><span class="line"><span>vrrp_instance VI_1 {</span></span>
<span class="line"><span>    state BACKUP</span></span>
<span class="line"><span>    interface eth0</span></span>
<span class="line"><span>    virtual_router_id 51</span></span>
<span class="line"><span>    priority 100</span></span>
<span class="line"><span>    advert_int 1</span></span>
<span class="line"><span></span></span>
<span class="line"><span>    unicast_src_ip 192.168.10.12</span></span>
<span class="line"><span>    unicast_peer {</span></span>
<span class="line"><span>        192.168.10.11</span></span>
<span class="line"><span>    }</span></span>
<span class="line"><span></span></span>
<span class="line"><span>    virtual_ipaddress {</span></span>
<span class="line"><span>        192.168.10.100/24 dev eth0</span></span>
<span class="line"><span>    }</span></span>
<span class="line"><span>}</span></span></code></pre></div><p>单播模式下两边的 <code>unicast_src_ip</code> 和 <code>unicast_peer</code> 要对称。防火墙也要放通两台入口之间的 VRRP 报文，抓包仍然可以看协议号 <code>112</code>：</p><div class="language-bash vp-adaptive-theme"><button title="Copy Code" class="copy"></button><span class="lang">bash</span><pre class="shiki shiki-themes github-light github-dark vp-code" tabindex="0"><code><span class="line"><span style="--shiki-light:#6F42C1;--shiki-dark:#B392F0;">tcpdump</span><span style="--shiki-light:#005CC5;--shiki-dark:#79B8FF;"> -nn</span><span style="--shiki-light:#005CC5;--shiki-dark:#79B8FF;"> -i</span><span style="--shiki-light:#032F62;--shiki-dark:#9ECBFF;"> eth0</span><span style="--shiki-light:#032F62;--shiki-dark:#9ECBFF;"> host</span><span style="--shiki-light:#005CC5;--shiki-dark:#79B8FF;"> 192.168.10.11</span><span style="--shiki-light:#032F62;--shiki-dark:#9ECBFF;"> or</span><span style="--shiki-light:#032F62;--shiki-dark:#9ECBFF;"> host</span><span style="--shiki-light:#005CC5;--shiki-dark:#79B8FF;"> 192.168.10.12</span></span>
<span class="line"><span style="--shiki-light:#6F42C1;--shiki-dark:#B392F0;">tcpdump</span><span style="--shiki-light:#005CC5;--shiki-dark:#79B8FF;"> -nn</span><span style="--shiki-light:#005CC5;--shiki-dark:#79B8FF;"> -i</span><span style="--shiki-light:#032F62;--shiki-dark:#9ECBFF;"> eth0</span><span style="--shiki-light:#032F62;--shiki-dark:#9ECBFF;"> proto</span><span style="--shiki-light:#005CC5;--shiki-dark:#79B8FF;"> 112</span><span style="--shiki-light:#6A737D;--shiki-dark:#6A737D;">  # VRRP 报文是否能互相看到</span></span></code></pre></div><h2 id="六、garp-和-arp-更新" tabindex="-1">六、GARP 和 ARP 更新 <a class="header-anchor" href="#六、garp-和-arp-更新" aria-label="Permalink to &quot;六、GARP 和 ARP 更新&quot;">​</a></h2><p>VIP 漂移以后，交换机、网关或客户端还可能短时间保留旧的 ARP 记录。表现是 VIP 已经在新 master 上，但部分客户端还往旧 MAC 发包。</p><p>Keepalived 成为 MASTER 时会发送 gratuitous ARP，用来刷新周围设备的 ARP 缓存。切换后短暂失败比较明显时，可以适当增加 GARP 次数：</p><div class="language-conf vp-adaptive-theme"><button title="Copy Code" class="copy"></button><span class="lang">conf</span><pre class="shiki shiki-themes github-light github-dark vp-code" tabindex="0"><code><span class="line"><span>vrrp_instance VI_1 {</span></span>
<span class="line"><span>    state MASTER</span></span>
<span class="line"><span>    interface eth0</span></span>
<span class="line"><span>    virtual_router_id 51</span></span>
<span class="line"><span>    priority 120</span></span>
<span class="line"><span>    advert_int 1</span></span>
<span class="line"><span></span></span>
<span class="line"><span>    garp_master_delay 1</span></span>
<span class="line"><span>    garp_master_repeat 5</span></span>
<span class="line"><span></span></span>
<span class="line"><span>    virtual_ipaddress {</span></span>
<span class="line"><span>        192.168.10.100/24 dev eth0</span></span>
<span class="line"><span>    }</span></span>
<span class="line"><span>}</span></span></code></pre></div><p>GARP 只能帮助刷新邻居缓存，不能替代客户端重连。长连接业务切换时仍然会有连接中断，入口高可用解决的是新请求入口，不是把已经断掉的 TCP 连接搬到另一台机器。</p><h2 id="七、抢占和非抢占" tabindex="-1">七、抢占和非抢占 <a class="header-anchor" href="#七、抢占和非抢占" aria-label="Permalink to &quot;七、抢占和非抢占&quot;">​</a></h2><p>默认情况下，高优先级节点恢复后可能重新抢回 MASTER。这个行为叫抢占。</p><p>非抢占配置：</p><div class="language-conf vp-adaptive-theme"><button title="Copy Code" class="copy"></button><span class="lang">conf</span><pre class="shiki shiki-themes github-light github-dark vp-code" tabindex="0"><code><span class="line"><span>vrrp_instance VI_1 {</span></span>
<span class="line"><span>    state BACKUP</span></span>
<span class="line"><span>    interface eth0</span></span>
<span class="line"><span>    virtual_router_id 51</span></span>
<span class="line"><span>    priority 120</span></span>
<span class="line"><span>    advert_int 1</span></span>
<span class="line"><span>    nopreempt</span></span>
<span class="line"><span></span></span>
<span class="line"><span>    virtual_ipaddress {</span></span>
<span class="line"><span>        192.168.10.100/24 dev eth0</span></span>
<span class="line"><span>    }</span></span>
<span class="line"><span>}</span></span></code></pre></div><p>生产里是否抢占要看业务。抢占能让主入口回到指定机器，但恢复后立刻切回也会带来一次连接抖动。维护窗口外，非抢占更安全——等确认状态稳定后再人工切，避免恢复动作本身造成第二次切换。</p><h2 id="八、检查-haproxy-或-nginx" tabindex="-1">八、检查 HAProxy 或 Nginx <a class="header-anchor" href="#八、检查-haproxy-或-nginx" aria-label="Permalink to &quot;八、检查 HAProxy 或 Nginx&quot;">​</a></h2><p>机器存活和入口可用是两件事。入口进程挂了但 Keepalived 还在，VIP 仍然可能留在坏节点上。</p><p>检查脚本：</p><div class="language-bash vp-adaptive-theme"><button title="Copy Code" class="copy"></button><span class="lang">bash</span><pre class="shiki shiki-themes github-light github-dark vp-code" tabindex="0"><code><span class="line"><span style="--shiki-light:#6A737D;--shiki-dark:#6A737D;"># /etc/keepalived/check_haproxy.sh</span></span>
<span class="line"><span style="--shiki-light:#6A737D;--shiki-dark:#6A737D;">#!/bin/bash</span></span>
<span class="line"><span style="--shiki-light:#005CC5;--shiki-dark:#79B8FF;">set</span><span style="--shiki-light:#005CC5;--shiki-dark:#79B8FF;"> -euo</span><span style="--shiki-light:#032F62;--shiki-dark:#9ECBFF;"> pipefail</span></span>
<span class="line"></span>
<span class="line"><span style="--shiki-light:#6F42C1;--shiki-dark:#B392F0;">pidof</span><span style="--shiki-light:#032F62;--shiki-dark:#9ECBFF;"> haproxy</span><span style="--shiki-light:#D73A49;--shiki-dark:#F97583;"> &gt;</span><span style="--shiki-light:#032F62;--shiki-dark:#9ECBFF;">/dev/null</span></span>
<span class="line"><span style="--shiki-light:#6F42C1;--shiki-dark:#B392F0;">ss</span><span style="--shiki-light:#005CC5;--shiki-dark:#79B8FF;"> -lntp</span><span style="--shiki-light:#D73A49;--shiki-dark:#F97583;"> |</span><span style="--shiki-light:#6F42C1;--shiki-dark:#B392F0;"> grep</span><span style="--shiki-light:#005CC5;--shiki-dark:#79B8FF;"> -q</span><span style="--shiki-light:#032F62;--shiki-dark:#9ECBFF;"> &#39;:80&#39;</span><span style="--shiki-light:#6A737D;--shiki-dark:#6A737D;">  # 确认入口端口还在监听</span></span></code></pre></div><p>授权：</p><div class="language-bash vp-adaptive-theme"><button title="Copy Code" class="copy"></button><span class="lang">bash</span><pre class="shiki shiki-themes github-light github-dark vp-code" tabindex="0"><code><span class="line"><span style="--shiki-light:#6F42C1;--shiki-dark:#B392F0;">chmod</span><span style="--shiki-light:#032F62;--shiki-dark:#9ECBFF;"> +x</span><span style="--shiki-light:#032F62;--shiki-dark:#9ECBFF;"> /etc/keepalived/check_haproxy.sh</span></span></code></pre></div><p>Keepalived 配置：</p><div class="language-conf vp-adaptive-theme"><button title="Copy Code" class="copy"></button><span class="lang">conf</span><pre class="shiki shiki-themes github-light github-dark vp-code" tabindex="0"><code><span class="line"><span>vrrp_script chk_haproxy {</span></span>
<span class="line"><span>    script &quot;/etc/keepalived/check_haproxy.sh&quot;</span></span>
<span class="line"><span>    interval 2</span></span>
<span class="line"><span>    fall 3</span></span>
<span class="line"><span>    rise 2</span></span>
<span class="line"><span>    weight -30</span></span>
<span class="line"><span>}</span></span>
<span class="line"><span></span></span>
<span class="line"><span>vrrp_instance VI_1 {</span></span>
<span class="line"><span>    state MASTER</span></span>
<span class="line"><span>    interface eth0</span></span>
<span class="line"><span>    virtual_router_id 51</span></span>
<span class="line"><span>    priority 120</span></span>
<span class="line"><span>    advert_int 1</span></span>
<span class="line"><span></span></span>
<span class="line"><span>    track_script {</span></span>
<span class="line"><span>        chk_haproxy</span></span>
<span class="line"><span>    }</span></span>
<span class="line"><span></span></span>
<span class="line"><span>    virtual_ipaddress {</span></span>
<span class="line"><span>        192.168.10.100/24 dev eth0</span></span>
<span class="line"><span>    }</span></span>
<span class="line"><span>}</span></span></code></pre></div><p><code>interval</code>、<code>fall</code>、<code>rise</code>、<code>weight</code> 的默认值：<code>interval</code> 默认 1 秒（不设时每秒执行一次），<code>fall</code> 默认 3（连续失败 3 次判定为不可用），<code>rise</code> 默认 2（连续成功 2 次判定为恢复），<code>weight</code> 默认 0（不调整优先级）。不设 <code>weight</code> 时脚本结果不会影响优先级，只能配合 <code>notify</code> 告警但不能触发切换。</p><p><code>weight -30</code> 表示脚本失败时优先级减 30。lb01 原来 120，失败后变 90，就会低于 lb02 的 100，让 VIP 漂过去。</p><h2 id="九、通知脚本" tabindex="-1">九、通知脚本 <a class="header-anchor" href="#九、通知脚本" aria-label="Permalink to &quot;九、通知脚本&quot;">​</a></h2><p>Keepalived 可以在状态变化时执行脚本：</p><div class="language-conf vp-adaptive-theme"><button title="Copy Code" class="copy"></button><span class="lang">conf</span><pre class="shiki shiki-themes github-light github-dark vp-code" tabindex="0"><code><span class="line"><span>vrrp_instance VI_1 {</span></span>
<span class="line"><span>    state MASTER</span></span>
<span class="line"><span>    interface eth0</span></span>
<span class="line"><span>    virtual_router_id 51</span></span>
<span class="line"><span>    priority 120</span></span>
<span class="line"><span>    advert_int 1</span></span>
<span class="line"><span></span></span>
<span class="line"><span>    notify_master &quot;/etc/keepalived/notify.sh MASTER&quot;</span></span>
<span class="line"><span>    notify_backup &quot;/etc/keepalived/notify.sh BACKUP&quot;</span></span>
<span class="line"><span>    notify_fault  &quot;/etc/keepalived/notify.sh FAULT&quot;</span></span>
<span class="line"><span></span></span>
<span class="line"><span>    virtual_ipaddress {</span></span>
<span class="line"><span>        192.168.10.100/24 dev eth0</span></span>
<span class="line"><span>    }</span></span>
<span class="line"><span>}</span></span></code></pre></div><p>脚本示例：</p><div class="language-bash vp-adaptive-theme"><button title="Copy Code" class="copy"></button><span class="lang">bash</span><pre class="shiki shiki-themes github-light github-dark vp-code" tabindex="0"><code><span class="line"><span style="--shiki-light:#6A737D;--shiki-dark:#6A737D;">#!/bin/bash</span></span>
<span class="line"><span style="--shiki-light:#005CC5;--shiki-dark:#79B8FF;">set</span><span style="--shiki-light:#005CC5;--shiki-dark:#79B8FF;"> -euo</span><span style="--shiki-light:#032F62;--shiki-dark:#9ECBFF;"> pipefail</span></span>
<span class="line"></span>
<span class="line"><span style="--shiki-light:#24292E;--shiki-dark:#E1E4E8;">state</span><span style="--shiki-light:#D73A49;--shiki-dark:#F97583;">=</span><span style="--shiki-light:#032F62;--shiki-dark:#9ECBFF;">&quot;</span><span style="--shiki-light:#005CC5;--shiki-dark:#79B8FF;">\${1</span><span style="--shiki-light:#D73A49;--shiki-dark:#F97583;">:-</span><span style="--shiki-light:#24292E;--shiki-dark:#E1E4E8;">UNKNOWN</span><span style="--shiki-light:#005CC5;--shiki-dark:#79B8FF;">}</span><span style="--shiki-light:#032F62;--shiki-dark:#9ECBFF;">&quot;</span></span>
<span class="line"><span style="--shiki-light:#6F42C1;--shiki-dark:#B392F0;">logger</span><span style="--shiki-light:#005CC5;--shiki-dark:#79B8FF;"> -t</span><span style="--shiki-light:#032F62;--shiki-dark:#9ECBFF;"> keepalived-notify</span><span style="--shiki-light:#032F62;--shiki-dark:#9ECBFF;"> &quot;state changed to \${</span><span style="--shiki-light:#24292E;--shiki-dark:#E1E4E8;">state</span><span style="--shiki-light:#032F62;--shiki-dark:#9ECBFF;">}&quot;</span></span></code></pre></div><p>通知脚本里可以接企业微信、邮件或告警系统。脚本要轻，避免状态切换时被通知逻辑卡住。</p><h2 id="十、与-lvs-配合" tabindex="-1">十、与 LVS 配合 <a class="header-anchor" href="#十、与-lvs-配合" aria-label="Permalink to &quot;十、与 LVS 配合&quot;">​</a></h2><p>Keepalived 可以直接管理 LVS virtual server 和 real server。</p><div class="language-conf vp-adaptive-theme"><button title="Copy Code" class="copy"></button><span class="lang">conf</span><pre class="shiki shiki-themes github-light github-dark vp-code" tabindex="0"><code><span class="line"><span>virtual_server 192.168.10.100 80 {</span></span>
<span class="line"><span>    delay_loop 3</span></span>
<span class="line"><span>    lb_algo rr</span></span>
<span class="line"><span>    lb_kind DR</span></span>
<span class="line"><span>    protocol TCP</span></span>
<span class="line"><span></span></span>
<span class="line"><span>    real_server 192.168.10.21 80 {</span></span>
<span class="line"><span>        weight 1</span></span>
<span class="line"><span>        TCP_CHECK {</span></span>
<span class="line"><span>            connect_timeout 3</span></span>
<span class="line"><span>            connect_port 80</span></span>
<span class="line"><span>        }</span></span>
<span class="line"><span>    }</span></span>
<span class="line"><span></span></span>
<span class="line"><span>    real_server 192.168.10.22 80 {</span></span>
<span class="line"><span>        weight 1</span></span>
<span class="line"><span>        TCP_CHECK {</span></span>
<span class="line"><span>            connect_timeout 3</span></span>
<span class="line"><span>            connect_port 80</span></span>
<span class="line"><span>        }</span></span>
<span class="line"><span>    }</span></span>
<span class="line"><span>}</span></span></code></pre></div><p>这样 Keepalived 不只做 VIP，还能根据健康检查维护 IPVS 后端。LVS + Keepalived 是传统四层入口里很常见的组合。</p><h2 id="十一、常见排查" tabindex="-1">十一、常见排查 <a class="header-anchor" href="#十一、常见排查" aria-label="Permalink to &quot;十一、常见排查&quot;">​</a></h2><p>检查 VIP：</p><div class="language-bash vp-adaptive-theme"><button title="Copy Code" class="copy"></button><span class="lang">bash</span><pre class="shiki shiki-themes github-light github-dark vp-code" tabindex="0"><code><span class="line"><span style="--shiki-light:#6F42C1;--shiki-dark:#B392F0;">ip</span><span style="--shiki-light:#032F62;--shiki-dark:#9ECBFF;"> addr</span><span style="--shiki-light:#032F62;--shiki-dark:#9ECBFF;"> show</span><span style="--shiki-light:#032F62;--shiki-dark:#9ECBFF;"> dev</span><span style="--shiki-light:#032F62;--shiki-dark:#9ECBFF;"> eth0</span><span style="--shiki-light:#D73A49;--shiki-dark:#F97583;"> |</span><span style="--shiki-light:#6F42C1;--shiki-dark:#B392F0;"> grep</span><span style="--shiki-light:#005CC5;--shiki-dark:#79B8FF;"> 192.168.10.100</span></span></code></pre></div><p>检查日志：</p><div class="language-bash vp-adaptive-theme"><button title="Copy Code" class="copy"></button><span class="lang">bash</span><pre class="shiki shiki-themes github-light github-dark vp-code" tabindex="0"><code><span class="line"><span style="--shiki-light:#6F42C1;--shiki-dark:#B392F0;">journalctl</span><span style="--shiki-light:#005CC5;--shiki-dark:#79B8FF;"> -u</span><span style="--shiki-light:#032F62;--shiki-dark:#9ECBFF;"> keepalived</span><span style="--shiki-light:#005CC5;--shiki-dark:#79B8FF;"> -n</span><span style="--shiki-light:#005CC5;--shiki-dark:#79B8FF;"> 100</span><span style="--shiki-light:#005CC5;--shiki-dark:#79B8FF;"> --no-pager</span></span></code></pre></div><p>抓 VRRP：</p><div class="language-bash vp-adaptive-theme"><button title="Copy Code" class="copy"></button><span class="lang">bash</span><pre class="shiki shiki-themes github-light github-dark vp-code" tabindex="0"><code><span class="line"><span style="--shiki-light:#6F42C1;--shiki-dark:#B392F0;">tcpdump</span><span style="--shiki-light:#005CC5;--shiki-dark:#79B8FF;"> -nn</span><span style="--shiki-light:#005CC5;--shiki-dark:#79B8FF;"> -i</span><span style="--shiki-light:#032F62;--shiki-dark:#9ECBFF;"> eth0</span><span style="--shiki-light:#032F62;--shiki-dark:#9ECBFF;"> proto</span><span style="--shiki-light:#005CC5;--shiki-dark:#79B8FF;"> 112</span><span style="--shiki-light:#6A737D;--shiki-dark:#6A737D;">  # VRRP 协议号是 112</span></span></code></pre></div><p>常见问题：</p><table tabindex="0"><thead><tr><th>现象</th><th>常见方向</th></tr></thead><tbody><tr><td>两台都没有 VIP</td><td>配置错误、网卡名错误、服务没启动</td></tr><tr><td>两台都有 VIP</td><td>VRRP 通信不通、防火墙拦截、virtual_router_id 冲突</td></tr><tr><td>切换后部分客户端不通</td><td>ARP 缓存没刷新、GARP 被网络设备限制</td></tr><tr><td>VIP 漂移但业务不通</td><td>HAProxy/Nginx 没监听、后端不可用</td></tr><tr><td>主恢复后又抢回</td><td>默认抢占行为</td></tr><tr><td>脚本不生效</td><td>权限、退出码、路径、SELinux</td></tr></tbody></table><p>Keepalived 排查里先看 VIP 在谁身上，再看 VRRP 报文是否互通，再看入口服务是否监听，最后看后端。比如 <code>ip addr</code> 已经看到 VIP 漂到备机，但 <code>ss -lntp</code> 没有 80/443 监听，客户端仍然会连不上；VIP 在、HAProxy/Nginx 也监听，但健康检查日志里后端全是 <code>DOWN</code>，入口地址已经恢复，问题就落到后端服务。</p>`,80)])])}const g=a(e,[["render",t]]);export{o as __pageData,g as default};
