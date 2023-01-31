# ArkAutoHR
明日方舟自动公开招募，使用adb控制安卓模拟器，实现公开招募的全自动

脚本使用python3编写

~~脚本依赖[cnocr](https://github.com/breezedeus/cnocr)与cv2等python库，请事先安装好~~

脚本需要将`adb.exe`所在文件夹加入环境变量

实现思路与运行效果参考此视频：https://www.bilibili.com/video/BV1jh411k7r9/

## 安装说明

### Anaconda虚拟环境（推荐）
为避免版本兼容问题，推荐使用Anaconda创建虚拟环境，具体步骤如下：
```
git clone https://github.com/shuangluoxss/ArkAutoHR
cd ArkAutoHR
conda create -n ArkAutoHR python=3.8 -y
conda activate ArkAutoHR
pip install https://download.lfd.uci.edu/pythonlibs/archived/Polygon3-3.0.9.1-cp38-cp38-win_amd64.whl
conda env update -f environment.yml
```
### pip直接安装
也可直接通过`pip`安装，步骤如下：
```
git clone https://github.com/shuangluoxss/ArkAutoHR
cd ArkAutoHR
pip install https://download.lfd.uci.edu/pythonlibs/archived/Polygon3-3.0.9.1-cp38-cp38-win_amd64.whl
pip install cnocr==2.2.2.1
```
注意：安装2.2版本的cnocr会自动附带`cnstd`, `pytorch`, `opencv`等库，占用空间较大，安装前请确保硬盘中用足够空间且与已有库不存在冲突

## 使用说明
1. 打开模拟器，运行明日方舟，并进入公开招募界面（如下图）
[公招界面](fig/公招界面.png)
2. 命令行输入`python auto_hr.py`运行脚本，可选参数：
```
  -h, --help            show this help message and exit
  -d Device_Name, --device Device_Name
                        设置ADB设备名称. eg. 127.0.0.1:5555（蓝叠模拟器）
  -n Num                设置本次需要公招的次数.
  -a, --all             公招直至龙门币、招聘许可或加急许可耗尽. 该选项将会覆盖[-n Num].
  -r, --reset           清除历史记录.
  -f, --force           无视检查，强制运行至指定次数或出错. (此选项可能有助于解决识别出错导致提前终止的问题)
  ```
3. 如果需要设置默认ADB设备名称或公招次数，请修改auto_hr.py第38行`devicename = '***'`或第50行`default_num = '***'`，如只需临时设置这两个参数可使用-d/--device及-n

注意：`干员信息.json`为截止到2023年1月31日为止的可公招干员信息，若后续新干员加入公招，此文件也需要更新
