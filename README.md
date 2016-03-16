shadowsocks
===========

一个 shadowsocks 服务器多账号管理系统，后端使用 shadowsocks-go 。支持多节点、流量限制等功能。


系统结构
----------

### 前台网站
    是一个 Django 项目，在需要更新账号信息时使用 xmlrpc 和同服务器的主节点通信。
	不要修改项目结构，按照一般的 Django 部署方式部署就行。目前不需要文件系统写权限。

### 主节点
    shadowsocks\master_node\master_node\master_server.py  文件。
	接受前台网站的请求更新各个节点账号数据，通信全部使用 xmlrpc 方式。
	这个需要和网站在同一服务器直接执行就行，不需要文件系统写权限。

### 子节点
    shadowsocks\ss_node\server.py 文件。
	部署在 shadowsocks-go 节点，直接执行就可以。
	但是需要 shadowsocks\config.json 的写权限已更新账号信息。
	流量统计功能需要root权限初始化一次。

### shadowsocks-go
    需要自己下载一个，然后和 shadowsocks\config.json 放在同一目录执行即可。
