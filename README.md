# ArkAutoHR
明日方舟自动公开招募，使用adb控制安卓模拟器，实现公开招募的全自动

脚本使用python3编写

~~脚本依赖[cnocr](https://github.com/breezedeus/cnocr)与cv2等python库，请事先安装好~~

脚本需要将`adb.exe`所在文件夹加入环境变量

实现思路与运行效果参考此视频：https://www.bilibili.com/video/BV1jh411k7r9/

## 安装说明
1. 使用`git clone`或Download Zip下载源代码
2. 命令行输入`pip install -r requirements.txt`安装python库
3. 如果安装完成后运行时出现`RuntimeError: Cannot find the MXNet library.`报错，并且使用的版本为python3.8则请尝试使用python3.6。[参考](https://github.com/apache/incubator-mxnet/issues/17719)
4. adb的安装请自行[百度](https://jingyan.baidu.com/article/22fe7cedf67e353002617f25.html)

## 使用说明
1. 打开模拟器，运行明日方舟，并进入公开招募界面（如下图）
[公招界面](fig/公招界面.png)
2. 命令行输入`python auto_hr.py`运行脚本，可选参数：
```
  -h, --help            show this help message and exit
  -d Device_Name, --device Device_Name
                        设置ADB设备名称. eg. 127.0.0.1:7555（网易MuMu模拟器）
  -n Num                设置本次需要公招的次数.
  -a, --all             公招直至龙门币、招聘许可或加急许可耗尽. 该选项将会覆盖[-n Num].
  -r, --reset           清除历史记录.
  -f, --force           无视检查，强制运行至指定次数或出错. (此选项可能有助于解决识别出错导致提前终止的问题)
  ```
3. 如果需要设置默认ADB设备名称或公招次数，请修改auto_hr.py第38行`devicename = '***'`或第50行`default_num = '***'`，如只需临时设置这两个参数可使用-d/--device及-n

注意：`干员信息.json`为截止到2021年2约20日位置的可公招干员信息，若后续新干员加入公招，此文件也需要更新

## 使用说明（原版）
1. 打开模拟器，运行明日方舟，并进入公开招募界面（如下图） 
[公招界面](fig/公招界面.png)
2. 命令行运行`adb devices`，找到模拟器对应的设备编号，将脚本第10行device_name修改为对应值 
[devices](fig/devices.png)
3. 将脚本12行num值修改为招募次数 
4. `python auto_hr.py`运行脚本 
