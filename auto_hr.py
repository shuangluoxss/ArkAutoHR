import os
import time
from cnocr import CnOcr, NUMBERS
from cv2 import imread
import numpy as np
from itertools import chain, combinations
import re
import json
import argparse

parser = argparse.ArgumentParser(description='明日方舟自动公招', add_help= True)
parser.add_argument('-d', '--device', metavar='Device_Name', help='设置ADB设备名称. eg. 127.0.0.1:7555（网易MuMu模拟器）')
parser.add_argument('-n', metavar='Num', type=int, help='设置本次需要公招的次数.')
parser.add_argument('-a', '--all', action='store_true', help='公招直至龙门币、招聘许可或加急许可耗尽. 该选项将会覆盖[-n Num].')
parser.add_argument('-r', '--reset', action='store_true', help='清除历史记录.')
parser.add_argument('-f', '--force', action='store_true', help='无视检查，强制运行至指定次数或出错. (此选项可能有助于解决识别出错导致提前终止的问题)')
args = parser.parse_args()

if (args.reset):
    try:
        os.remove('history.log')
        print('history.log已清除')
    except:
        print('未找到history.log，跳过')
    try:
        for root, dirs, files in os.walk('screenshots', topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
            for name in dirs:
                os.rmdir(os.path.join(root, name))
        os.rmdir('screenshots')
        print('screenshots已清除')
    except:
        print('未找到screenshots，跳过')
    exit()

# 模拟器device_name，使用adb devices查看
device_name = '127.0.0.1:7555' #网易MuMu模拟器
#device_name = '127.0.0.1:62026'
#device_name = '127.0.0.1:5555' #雷电模拟器
if (args.device):
    device_name = args.device
# 连接adb
adb_devices = os.popen('adb devices').read()
if device_name not in adb_devices:
    print('Trying to connent to %s' % device_name)
    os.popen('adb connect %s' % device_name).read()

# 公招次数
default_num = 114514
if (args.all):
    num = default_num
elif (args.n):
    num = args.n
else:
    num = input('请输入要公招的次数(直接回车则运行至材料耗尽)：')
    if (num):
        num = int(num)
    else:
        num = default_num

'''
模拟器分辨率默认为960*540，若为其他分辨率，调整factor
如分辨率为1280*720，则factor=1280/960
仅支持16:9分辨率，其他分辨率请自行调整recognize_tag与gongzhao中坐标参数
'''
if not os.path.exists('screenshots'):
    os.mkdir('screenshots')
os.popen('adb -s %s shell screencap -p /sdcard/01.png' % device_name).read()
os.popen('adb -s %s pull /sdcard/01.png screenshots/resolution_test.png' % (device_name)).read()
img = imread('screenshots/resolution_test.png')
os.remove('screenshots/resolution_test.png')
factor = img.shape[1] / 960

ocr = CnOcr()

with open('干员信息.json', 'r', encoding='utf-8') as file:
    op_dict = json.loads(file.read())
tag_dict = {}
reg_dict = {}
for name, info in op_dict.items():
    tag_list = info['tags']
    star = info['星级']
    tag_list.append(info['职业'] + '干员')
    if star == 2:
        tag_list.append('新手')
    elif star == 5:
        tag_list.append('资深干员')
    elif star == 6:
        tag_list.append('高级资深干员')
    for tag in tag_list:
        if tag in tag_dict:
            tag_dict[tag].add(name)
        else:
            tag_dict[tag] = {name}
    reg_dict[info['报到']] = name

def force_or_exit(errmsg = '遇到错误，退出...'):
    if (args.force):
        print('--force选项启用，尝试继续运行')
        return None
    print(errmsg)
    exit()

def str_similiar(s1, s2):
    """
    返回字符串s1与字符串s2的相似程度
    """
    score = 0
    max_len = min(len(s1), len(s2))
    if s1[:max_len] == s2[:max_len]:
        score += 100 ** max_len
    for sub_str_len in range(1, 6):   #字串长度1至5
        s1_set = set([s1[i:i+sub_str_len] for i in range(len(s1) + 1 - sub_str_len)])
        s2_set = set([s2[i:i+sub_str_len] for i in range(len(s2) + 1 - sub_str_len)])
        score += len(s1_set & s2_set) * 10 ** sub_str_len
    return score

def search_in_list(s_list, x, min_score=1000):
    """
    寻找字符串数组s_list中与字符串x最接近的字符串并返回。若相似度不高或有两个字符串相似度相同，返回None
    """
    tmp_list = [(s, str_similiar(s, x)) for s in s_list]
    tmp_list.sort(key=lambda x: x[1], reverse=True)
    if tmp_list[0][1] > max(min_score, tmp_list[1][1]):
        return tmp_list[0]
    else:
#         print(x, tmp_list[:3])
        return None, 0

def img_to_tag(tag_img):
    """
    识别图片tag_img中的tag，若识别失败则返回False
    """
    tag = mat_tostring(ocr.ocr(tag_img))
    #只保留中文字符
    tag = re.sub(r'[^\u4e00-\u9fa5]', '', tag)
    if tag in tag_dict:    #识别成功，直接返回tag
        return tag
    else:                  #识别失败，返回搜索结果
        tag_fix, score = search_in_list(tag_dict, '术师于员', 100)
        if score > 100:
            return tag_fix
        else:
            raise ValueError('无法识别tag')

def get_score(tag_list):
    """
    计算某tag组合的分值：首先将满足各tag的干员取交集得到最终可能获得的干员列表，可能的最低星级*100减去tag数量作为分数
    由于拉满9小时最低三星，因此最低星级锁定为3星
    """
    if len(tag_list) == 0:
        return 300 + 5
    possible_result = tag_dict[tag_list[0]]
    for i in range(1, len(tag_list)):
        possible_result = possible_result & tag_dict[tag_list[i]]
    possible_result = set(filter(lambda x: 3 <= op_dict[x]['星级'] < (6 if '高级资深干员' not in tag_list else 7), possible_result))
    if possible_result != set():
        star_min = min([op_dict[name]['星级'] for name in possible_result])
        star_max = max([op_dict[name]['星级'] for name in possible_result])
        score = star_min * 100 - 10 * len(tag_list) + star_max
        return score
    else:
        return 0

def choose_tags(tag_list):
    """
    对于给定的5个tag，遍历其中不超过3个tag的所有组合，按照分值从大到小排序，返回分值最高的tag组合
    """
    all_possible_comb = []
    for i in range(4):
        all_possible_comb.extend(list(combinations(tag_list, i)))
    all_possible_comb.sort(key=get_score, reverse=True)
    return all_possible_comb[0]

def recognize_tag(screenshot):
    """
    从截图中取5个tag对应的位置，分别识别tag内容并给出最优选择
    """
    #5个tag对应的位置，由截图规格决定
    x = np.array(np.round(np.array([281, 406, 532, 281, 406]) * factor), dtype=int)
    y = np.array(np.round(np.array([278, 278, 278, 332, 332]) * factor), dtype=int)
    dx = int(109 * factor)
    dy = int(18 * factor)
    tag_list = [img_to_tag(255 - screenshot[y[i]:y[i]+dy,x[i]:x[i]+dx]) for i in range(5)]
    if False in tag_list:
        raise ValueError('tag识别失败！')
    else:
        tags_choosen = choose_tags(tag_list)
        tag_to_index = dict(zip(tag_list, range(5)))
        return tag_list, tags_choosen, [tag_to_index[tag] for tag in tags_choosen]

def mat_tostring(mat):
    return ''.join(list(chain.from_iterable(mat)))

def recognize_name(screenshot):
    """
    从截图中取报到语音对应的位置，根据语音内容识别干员
    """
    reg_voice = mat_tostring(ocr.ocr(255 - screenshot[int(480*factor):, int(150*factor):int(-130*factor)]))
#     print(reg_voice)
    voice, score = search_in_list(reg_dict, reg_voice)
    if voice is not None:
        return reg_dict[voice], score
    else:
        return None

def load_image(filename):
    screenshot = imread('screenshots/' + filename)
    if screenshot is not None:
        return screenshot
    else:
        raise NameError

def check_ticket(screenshot):
    ocr.set_cand_alphabet(cand_alphabet=NUMBERS)
    item = mat_tostring(ocr.ocr_for_single_line(254 - screenshot[int(496*factor):int(513*factor), int(385*factor):int(440*factor)]))
    ocr.set_cand_alphabet(cand_alphabet=None)
    item = re.sub(r'[^0-9]', '', item)[:-1]
    print('剩余公招许可：%s' % item)
    if (item == '0'):
        force_or_exit('招聘许可不足，退出...')
    return None

def read_prompt(screenshot):
    prompt = mat_tostring(ocr.ocr(255 - screenshot[int(50*factor):int(120*factor), int(775*factor):]))
    prompt, score = search_in_list(['龙门币不足', '招聘许可不足', '加急许可不足'], prompt)
    if (prompt is not None):
        force_or_exit('%s，退出...' % prompt)
    return None

def gongzhao(num, start=0):
    pos_dict = {
        '新建': (243, 217),
        '增加时长':(340, 110),
        'tag': ((338, 290), (464, 290), (587, 290), (338, 341), (464, 341)),
        '招募': (733, 436),
        '加急': (353, 287),
        '确认': (720, 381),
        '聘用': (240, 285),
        'skip': (917, 30)
    }
    def click(pos, sleep=0.5):
        command = 'adb -s %s shell input tap %d %d' % (device_name, int(pos[0] * factor), int(pos[1] * factor))
    #     print(command)
        os.system(command)
        time.sleep(sleep)
    # 提前录制点击增加时长按钮的操作，保存在/sdcard/record1，可提高adb点击速度
    def click_incre():
        for i in range(8):
            os.popen('adb -s %s shell dd if=/sdcard/record1 of=/dev/input/event4' % device_name).read()
    def screenshot(filename):
        os.popen('adb -s %s shell screencap -p /sdcard/01.png' % device_name).read()
        os.popen('adb -s %s pull /sdcard/01.png screenshots/%s' % (device_name, filename)).read()

    for k in range(start, start + num):
        print('\n本次第%d抽，累计第%d抽' % (k-start+1, k))
        click(pos_dict['新建'], 1)
        screenshot('tag_%d.png' % k)
        #检测公招券道具数量
        check_ticket(load_image('tag_%d.png' % k))
#         click_incre()
        for i in range(8):
            click(pos_dict['增加时长'], 0)
        tag_list, tags_choosen, click_pos = recognize_tag(load_image('tag_%d.png' % k))
        print('\t可选tag为：\t' + ', '.join(tag_list))
        if ('高级资深干员' in tag_list):
            force_or_exit('出现高级资深干员，请人工选择，退出...')
        print('\t选择tag为：\t' + ', '.join(tags_choosen))
        for i in click_pos:
            click(pos_dict['tag'][i], 0.1)
        click(pos_dict['招募'], 2)
        screenshot('tmp.png')
        read_prompt(load_image('tmp.png'))
        click(pos_dict['加急'], 1.5)
        screenshot('tmp.png')
        read_prompt(load_image('tmp.png'))
        click(pos_dict['确认'], 2)
        click(pos_dict['聘用'], 1)
        click(pos_dict['skip'], 3)
        screenshot('result_%d.png' % k)
        name, score = recognize_name(load_image('result_%d.png' % k))
        if name in op_dict:
            print('\t获得干员为：\t %d★%s' % (op_dict[name]['星级'], name))
        else:
            print('\t获得干员为：\t 未识别')
        with open('history.log', 'a+', encoding='utf-8') as file:
            file.write('%d; %s; %s; %s; %d\n' % (k, str(tag_list), str(tags_choosen), name, op_dict[name]['星级']))
        click(pos_dict['skip'])
        click(pos_dict['skip'])
    print('\n已完成%d次公招，退出...' % num)

if __name__ == '__main__':
    try:
        start = max([int(x) for x in re.findall(r'result_(\d+).png',
                    '\n'.join(os.listdir('screenshots')))]) + 1
    except:
        start = 1
    gongzhao(num, start)