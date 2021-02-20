# ArkAutoHR
明日方舟自动公开招募，使用adb控制安卓模拟器，实现公开招募的全自动  
脚本使用python3编写  
脚本依赖[cnocr](https://github.com/breezedeus/cnocr)与cv2等python库，请事先安装好  
脚本需要将`adb.exe`所在文件夹加入环境变量  
实现思路与运行效果参考此视频：https://www.bilibili.com/video/BV1jh411k7r9/

## 使用说明
1. 打开模拟器，运行明日方舟，并进入公开招募界面（如下图） 
[公招界面](fig/公招界面.png)
2. 命令行运行`adb devices`，找到模拟器对应的设备编号，将脚本第10行device_name修改为对应值 
[devices](fig/devices.png)
3. 将脚本12行num值修改为招募次数 
4. `python auto_hr.py`运行脚本 

注意：`干员信息.json`为截止到2021年2约20日位置的可公招干员信息，若后续新干员加入公招，此文件也需要更新
