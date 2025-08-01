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



### 4.给指定机器部署操作系统
```shell
ansible-playbook playbooks/deploy_os.yaml -e "hostname=maas02 os=24.04"
```
#### 支持的参数包括：
hostname：       **必要参数**，string类型，要部署的主机名称
os：             **必要参数**，string类型，部署的操作系统,举例说明，如果要部署Jammy Jellyfish使用：**ubuntu/jammy, jammy and ubuntu/22.04, 22.04**
install_rack:   **可选参数**，bool类型，默认false，设置为true时会安装rack组件，并自动注册到maas中
install_kvm:    **可选参数**，bool类型，默认false，设置为true时会安装KVM组件，并自动注册到maas中
install_vmhost: **可选参数**，bool类型，默认false，设置为true时会按照LXD组件，并自动注册到maas中
user_data：      **可选参数**，string类型，默认为空，如需使用，指定user_data文件路径即可。
#### 使用限制：
只能对Ready状态和Release状态的机器进行部署，因为maas本身的bug，有时候hostname正确也会报404错误，这个时候建议先对机器执行commissioning然后再部署，否则可能会出现客户端正常部署完成，但是服务端一直显示部署中。

### 5.修改机器状态
```shell
ansible-playbook playbooks/change_machine_status.yaml -e "hostname=client01 target_state=released"
```


#### 支持的参数包括：
hostname：       **必要参数**，string类型，要修改的主机
target_state：   **必要参数**，string类型，要修改的为的状态，支持的值包括locked（op-lock）、unlocked（op-unlock）、broken（op-mark_broken)、fixed（op-mark_fixed）、 released（op-release）、commissioning（op-commission）、rescue_mode（op-rescue_mode）、exit_rescue（op-exit_rescue_mode）、power_on（op-power_on）、power_off（op-power_off）

#### 注意事项 
如果机器部署为kvm状态，释放时会报错，某些状态间不允许直接切换，自行阅读官方文档

### 6.删除机器
```shell
ansible-playbook playbooks/change_machine_status.yaml -e "hostname=client01"
```
#### 支持的参数
hostname:    **必要参数**， string类型，指定要从maas中删除的主机

## 注意事项
本项目通过 Ansible 调用 MAAS API，与 Web 界面操作具有同等效果。

若使用 sudo 切换用户运行脚本，请确保正确传递环境变量（推荐 sudo -E 或直接登录用户环境）。

## 贡献说明
欢迎提交 PR 或 Issue！使用建议、功能请求、Bug 反馈都很有价值。

## License
本项目采用 MIT 许可证，详见 LICENSE 文件。

如果你需要，我还可以帮你生成 .gitignore、LICENSE 文件，或者把这个 README 渲染成 GitHub 风格页面截图。如果现在可以了，建议你可以直接把这份内容命名为 README.md 上传到 GitHub 仓库中。是否需要我帮你生成最终文件？


