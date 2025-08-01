## 项目简介
本项目的主要作用是通过ansible调用conical公司旗下maas的api，从而对裸金属进行管理。本项目在maas3.5和maas3.6中测试通过。

## 使用简介
### 1.安装和配置相关依赖
本项目需登录maas管理平台获取api_key，在groups_vars/all.yaml文件中将maas_url和api_key变量修改为相应的值。
```shell
pip3 install -r requirements.txt
```

### 2.向maas中添加机器
```shell
ansible-playbook playbooks/add_machine.yaml -e "hostname=maas02 mac_address=00:0C:29:18:9D:4C ip_address=192.168.157.250"
```
执行如上命令可以将机器裸金属添加到maas平台，并且将设置的ip和mac地址做静态dhcp绑定，因此在后续使用过程中机器状态发生变化也能分配相同的ip地址，确保机器全生命周期内ip、主机名、mac绑定关系的唯一性。

playbook添加机器的电源模式为manual，可以在使用时候根据需求改成相应的模式，并增加相应的模式的参数。默认机器添加后所在的zone为local_zone、pool为，bare，可以根据需求修改变量
**前置条件**
a.在执行添加机器之前需配置好机器的ipmi、virsh、pve等相关信息；
b.机器只有一张网卡启用了pxe功能；
c、预先知道启用了pxe网卡的mac地址，预先规划了机器的主机名；

### 3.从maas中获取机器列表
```shell
ansible-playbook  playbooks/get_machines.yaml
```
执行如上命令可获取maas中所有机器的列表，并且按照区域和状态进行分组，显示主机fqdn、ip地址、状态、区域、池、操作系统等信息

### 4.获取指定机器的信息
```shell
ansible-playbook  playbooks/get_machine_info.yaml -e hostname=maas02
```
打印的信息包括主机名、状态、IP地址、系统、区域、池、CPU、内存、磁盘、MAC地址、启动方式、主板厂商、主板型号、系统厂商等

