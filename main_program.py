import os
import queue
from tabnanny import check
from time import sleep
from urllib.parse import uses_params

from moviepy import VideoFileClip
import numpy as np
from pygame import surface, Surface
from pygame.event import clear
from pygame.examples.music_drop_fade import volume

os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'

import time
import math
import pygame as pg
import os
import threading
import random

# 尝试导入其他模块
try:
    import stellar_evolution_engine as star
except ImportError:
    star = None
    print("警告：未找到stellar_evolution_engine模块")

pg.init()
# 屏幕设置
screen = pg.display.set_mode((960, 720))
pg.display.set_caption('行星球宇宙-Universe of PlanetBall')
pg.mixer.music.load("./Resources/music/SubstituteForSunrise.wav")
pg.mixer.music.play(-1)
icon = pg.image.load("./Resources/assets/icon/icon.jpg")
pg.display.set_icon(icon)

# 加载背景图片
menu_background = None
background_01 = None
background_02 = None
background_03 = None
background_04 = None
background_06 = None
background_07 = None
background_08 = None
background_09 = None

try:
        menu_background = pg.image.load("./Resources/assets/background_files/background_menu.jpg")
        menu_background = pg.transform.scale(menu_background, (960, 720))
except Exception as e:
        print(f"加载菜单背景失败: {e}")
        menu_background = pg.Surface((960, 720))
        menu_background.fill((10, 10, 30))
try:
    selected_background = pg.image.load("./Resources/assets/background_files/background_01.jpg")
    selected_background = pg.transform.scale(selected_background, (960, 720))
except Exception as e:
    print(f"加载引擎背景失败: {e}")
    selected_background = pg.Surface((960, 720))
    selected_background.fill((20, 10, 40))



# 设置当前背景
current_background = menu_background
is_in_engine_mode = False
is_in_selecting_evo = False
volume_status = False
credits_status = False
evolution_pattern = False
music1 = True
music2 = False
music3 = False# 标记是否在引擎,选择背景模式

# 字体设置 - 使用支持中文的字体
font_paths = [
    "C:/Windows/Fonts/simhei.ttf",  # Windows 黑体
    "C:/Windows/Fonts/simsun.ttc",  # Windows 宋体
    "./Resources/fonts/simhei.ttf",  # 尝试项目目录中的字体
]

font = None
for path in font_paths:
    try:
        if os.path.exists(path):
            font = pg.font.Font(path, 28)
            print(f"使用字体: {path}")
            break
    except:
        continue

# 如果找不到中文字体，使用默认字体
if font is None:
    print("警告：未找到中文字体，将使用默认字体")
    font = pg.font.Font(None, 28)

# 创建不同大小的字体
title_font = pg.font.Font(None, 48) if font is None else pg.font.Font(
    font_paths[0] if os.path.exists(font_paths[0]) else None, 48)
subtitle_font = pg.font.Font(None, 32) if font is None else pg.font.Font(
    font_paths[0] if os.path.exists(font_paths[0]) else None, 32)
small_font = pg.font.Font(None, 24) if font is None else pg.font.Font(
    font_paths[0] if os.path.exists(font_paths[0]) else None, 24)
input_font = pg.font.Font(None, 26) if font is None else pg.font.Font(
    font_paths[0] if os.path.exists(font_paths[0]) else None, 26)




# 输入框类
class InputBox:
    def __init__(self, x : int, y : int, width : int, height : int, label : str, text_x : int, default_value="", tooltip=""):#inputbox总参数框
        self.rect = pg.Rect(x, y, width, height)#定义输入框为pg的输入框，相关参数
        self.label = label#给每个不同的输入框起个名字
        self.text_x = text_x#这个表示你输入文字的时候，文字的起始位置，距离输入框左侧
        self.text = default_value#初始化每个输入框的内容，保证每次输入是空的
        self.tooltip = tooltip#鼠标悬停在输入框上的时候，它的提示信息
        self.active = False#应该是激活与否，一开始肯定不可以激活啊，点击后才激活，用户可以输入。
        self.label_surf = font.render(label, True, (200, 200, 255))#人话，让每个输入框上方显示自己的名字，包括了文字颜色，不然你知道这个输入框干蛋的哈哈哈？
        self.text_surf = input_font.render(self.text, True, (255, 255, 255))#你输入文字的颜色哈哈哈，antialias是抗锯齿，优化文字显示的

    def handle_event(self, event):
        if event.type == pg.MOUSEBUTTONDOWN:#MOUSEBUTTONDOWN是指的鼠标点击事件，这句话的意思不言自明了吧_smile
            if self.rect.collidepoint(event.pos):
                self.active = True#点击在输入框矩形内激活输入框
            else:
                input_boxes[2].tooltip = f"范围: 0.001-恒星寿命的80%（{star.get_tau(input_boxes[0].get_value(), input_boxes[1].get_value()) * 0.8}）"
                self.active = False#乱点就滚，没有用，木大木大！

        if event.type == pg.KEYDOWN:#哥们你终于TM（商标缩写，没骂人）知道给输入框输入文字了
            if self.active:#这句话是说，只有输入框被激活让你输入你输入才有效，你永远救不活装死的人
                if event.key == pg.K_RETURN:#你按回车了，输入框又睡着了但是内容保存了，其实就是你回车了就表示输入完成，可以滚了哈哈哈
                    input_boxes[2].tooltip = f"范围: 0.001-恒星寿命的80%（{star.get_tau(input_boxes[0].get_value(), input_boxes[1].get_value()) * 0.8}）"
                    self.active = False
                elif event.key == pg.K_BACKSPACE:#这句话就是你如果迷糊打错字了，给你个机会删了C重写，按一下back就删除一个
                    self.text = self.text[:-1]
                elif event.key == pg.K_v and (pg.key.get_mods() & pg.KMOD_CTRL):#你可以使用快捷键，懒汉福利
                    clipboard_text = pg.scrap.get(pg.SCRAP_TEXT)
                    if clipboard_text:
                        self.text += clipboard_text.decode('utf-8', errors='ignore')#乱按不是字母的组合键而且莫得快捷键意义，就给老子爬！
                else:# 处理普通字符输入（字母、数字、符号）
                     # 这里根据不同的输入框类型，限制能输入什么字符
                    # 根据不同的输入框限制输入
                    if self.label.startswith("恒星质量"):
                        # 只允许数字和小数点
                        if event.unicode.isdigit() or event.unicode == '.':
                            self.text += event.unicode
                    elif self.label.startswith("金属度"):
                        # 只允许数字和小数点
                        if event.unicode.isdigit() or event.unicode == '.':
                            self.text += event.unicode
                    elif self.label.startswith("演化终点") or self.label.startswith("演化步长"):
                        # 只允许数字和小数点
                        if event.unicode.isdigit() or event.unicode == '.':
                            self.text += event.unicode
                    elif self.label.startswith("刷新间隔"):
                        # 允许数字和小数点
                        if event.unicode.isdigit() or event.unicode == '.':
                            self.text += event.unicode
                    elif self.label.startswith("音量"):
                        if event.unicode.isdigit() or event.unicode == '.':
                            self.text += event.unicode

                self.text_surf = input_font.render(self.text, True, (255, 255, 255))

    def draw(self, screen):
        # 把每个输入框的名字（label）写上
        screen.blit(self.label_surf, (self.text_x, self.rect.y))

        # 绘制输入框
        color = (60, 60, 80, 200) if not self.active else (80, 80, 100, 220)
        input_surface = pg.Surface((self.rect.width, self.rect.height), pg.SRCALPHA)
        pg.draw.rect(input_surface, color, (0, 0, self.rect.width, self.rect.height), border_radius=5)
        pg.draw.rect(input_surface, (255, 255, 255, 150) if not self.active else (100, 200, 255, 200),
                     (0, 0, self.rect.width, self.rect.height), width=2, border_radius=5)

        screen.blit(input_surface, self.rect)

        # 绘制文字，渲染你打进去的字
        text_x = self.rect.x + 10
        text_y = self.rect.y + (self.rect.height - self.text_surf.get_height()) // 2
        screen.blit(self.text_surf, (text_x, text_y))

        # 绘制光标
        if self.active and int(time.time() * 2) % 2 == 0:
            cursor_x = text_x + self.text_surf.get_width() + 2
            pg.draw.line(screen, (255, 255, 255),
                         (cursor_x, text_y),
                         (cursor_x, text_y + self.text_surf.get_height()), 2)

    def get_value(self):
        """获取输入框的值，转换为浮点数"""
        try:
            return float(self.text) if self.text else 0.0
        except ValueError:
            return 0.0

    def draw_tooltip(self, screen, mouse_pos):#你傻了不知道每个输入框的输入规则，这里会告诉你
        """绘制工具提示"""
        if self.rect.collidepoint(mouse_pos) and self.tooltip:#你点了输入框
            tooltip_surf = small_font.render(self.tooltip, True, (255, 255, 200))#提示框文字属性
            tooltip_bg = pg.Surface((tooltip_surf.get_width() + 10,  # 加10像素边距
                                     tooltip_surf.get_height() + 10),
                                    pg.SRCALPHA)  # 使用透明通道
            tooltip_bg.fill((0, 0, 0, 200))
            screen.blit(tooltip_bg, (mouse_pos[0], mouse_pos[1] - 30))
            screen.blit(tooltip_surf, (mouse_pos[0] + 5, mouse_pos[1] - 25))

# 按钮类
class Button:
    def __init__(self, x, y, width, height, text, color=(0, 0, 0, 100), hover_color=(120, 120, 120, 200)):
        self.rect = pg.Rect(x, y, width, height)#同上，输入框，给对应函数内参数赋值
        self.text = text
        self.color = color
        self.hover_color = hover_color#按钮是什么颜色？天空是蔚蓝色，窗外有千纸鹤~~
        self.current_color = color #按钮当前的颜色，你问这是干啥的，多此一举？汝安之鱼之乐（当然我肯定比鱼聪明）？这个就是你按钮悬停与否有俩状态颜色，定义个中间商
        self.text_surf = font.render(text, True, (255, 255, 255))
        self.text_rect = self.text_surf.get_rect(center=self.rect.center)#bro先说好了啊，到时候在按钮中间写字，别瞎写写飞了到时候不如他妈八岁小男孩写的整齐

    def draw(self, surface):#告诉这个傻子电脑，每个按钮的边框怎么画
        button_surface = pg.Surface((self.rect.width, self.rect.height), pg.SRCALPHA)#按钮边框
        pg.draw.rect(button_surface, self.current_color,
                     (0, 0, self.rect.width, self.rect.height),
                     border_radius=10)
        pg.draw.rect(button_surface, (255, 255, 255, 100),
                     (0, 0, self.rect.width, self.rect.height),
                     width=2, border_radius=10)

        surface.blit(button_surface, self.rect)#对应每个按钮画到屏幕上的规则，边框和矩形本身
        surface.blit(self.text_surf, self.text_rect)#按钮的文字不画按钮上你知道和这个按钮在搞什么飞机吗？心电感应吗？

    def check_hover(self, pos):  # pos是鼠标位置(x, y)
        if self.rect.collidepoint(pos):  # 修复了这里的缩进错误
            # 摸到了！换漂亮衣服 💃
            self.current_color = self.hover_color
            return True  # 报告："我在被摸！"
        else:
            self.current_color = self.color
            return False

    def check_click(self, pos, event):#诶，这里就是看看你点没点按钮了
        if self.rect.collidepoint(pos) and event.type == pg.MOUSEBUTTONDOWN and event.button == 1:#鼠标在按钮上而且点了它才可以，隔山打牛的请离开谢谢
            return True#你好好点了才管用
        return False#再乱玩就玩坏了


# 返回按钮类
class ReturnButton:#和上面哪里俩逻辑一样，这是返回按钮。你要是点进去了出不来他妈卡进后室了是吧
    def __init__(self, x, y, width, height, text):
        self.rect = pg.Rect(x, y, width, height)
        self.text = text
        self.color = (50, 50, 50, 150)
        self.hover_color = (80, 80, 80, 180)
        self.current_color = self.color
        self.text_surf = font.render(self.text, True, (255, 255, 255))
        self.text_rect = self.text_surf.get_rect(center=self.rect.center)

    def draw(self, surface):#一样你得告诉这个不太聪明的电脑这类按钮怎么画，你要和机器一样傻了，你就是人体机器，简称人机
        button_surface = pg.Surface((self.rect.width, self.rect.height), pg.SRCALPHA)
        pg.draw.rect(button_surface, self.current_color,
                     (0, 0, self.rect.width, self.rect.height),
                     border_radius=8)
        pg.draw.rect(button_surface, (255, 255, 255, 80),
                     (0, 0, self.rect.width, self.rect.height),
                     width=1, border_radius=8)

        surface.blit(button_surface, self.rect)#把这类按钮画到屏幕上，不然只有规则纸上谈兵。赵括都得拜您为师
        surface.blit(self.text_surf, self.text_rect)

    def check_hover(self, pos):#一样检查点没点，悬停与否
        if self.rect.collidepoint(pos):
            self.current_color = self.hover_color#这个是悬停的颜色，用户体验这一块~
            return True
        else:
            self.current_color = self.color#没放上去颜色不变，不然按钮TM闹鬼了
            return False

    def check_click(self, pos, event):
        if self.rect.collidepoint(pos) and event.type == pg.MOUSEBUTTONDOWN and event.button == 1:#一样点没点
            return True
        return False


class Background_select_button:
    def __init__(self, x: int, y: int, width: int, height: int, label: str):
        self.rect = pg.Rect(x, y, width, height)
        self.label = label

        self.color = (0, 0, 0, 100 )
        self.hover_color = (80, 80, 80, 180)
        self.current_color = self.color

        self.font = pg.font.Font(None, 20) if font is None else pg.font.Font(font_paths[0] if os.path.exists(font_paths[0]) else None, 20)
        self.label_surf = self.font.render(self.label, True, (255, 255, 255))  # ✅ 改成 self.font
        self.label_rect = self.label_surf.get_rect(center=(x + width // 2, y + height // 2))  # ✅ 居中显示在按钮下方

    def draw(self, surface):
        button_surface = pg.Surface((self.rect.width, self.rect.height), pg.SRCALPHA)
        pg.draw.rect(button_surface, self.current_color,
                     (0, 0, self.rect.width, self.rect.height),
                     border_radius=8)
        pg.draw.rect(button_surface, (255, 255, 255, 80),
                     (0, 0, self.rect.width, self.rect.height),
                     width=1, border_radius=8)

        surface.blit(button_surface, self.rect)  # 把这类按钮画到屏幕上，不然只有规则纸上谈兵。赵括都得拜您为师
        surface.blit(self.label_surf, self.label_rect)

    def check_hover(self, mouse_pos):  # ✅ 加上悬停检测方法
        if self.rect.collidepoint(mouse_pos):
            self.current_color = self.hover_color
            return True
        else:
            self.current_color = self.color
            return False

    def check_click(self, mouse_pos, event):  # ✅ 加上点击检测方法
        if (self.rect.collidepoint(mouse_pos) and
                event.type == pg.MOUSEBUTTONDOWN and
                event.button == 1):
            return True
        return False

class Text:
    def __init__(self, x, y, width, height, text):
        self.rect = pg.Rect(x, y, width, height)
        self.text_surf = font.render(text, True, (255, 255, 255))
        self.text_rect = self.text_surf.get_rect(center=self.rect.center)

    def render(self):
        screen.blit(self.text_surf, self.text_rect)

    def set_text(self, text):
        self.text_surf = font.render(text, True, (255, 255, 255))

star_4000_5000_img = pg.image.load("./Resources/assets/blackbody_color/4000K_5000K.png")
star_5000_5500_img = pg.image.load("./Resources/assets/blackbody_color/5000K_5500K.png")
star_5500_6000_img = pg.image.load("./Resources/assets/blackbody_color/5500K_6000K.png")
star_6000_7500_img = pg.image.load("./Resources/assets/blackbody_color/6000K_7500K.png")
star_7500_9000_img = pg.image.load("./Resources/assets/blackbody_color/7500K_9000K.png")
star_9000_12000_img = pg.image.load("./Resources/assets/blackbody_color/9000K_12000K.png")
pg.transform.scale(star_4000_5000_img, (1332, 750))
pg.transform.scale(star_5000_5500_img, (1332, 750))
pg.transform.scale(star_5500_6000_img, (1332, 750))
pg.transform.scale(star_6000_7500_img,(1332, 750))
pg.transform.scale(star_7500_9000_img,(1332, 750))
pg.transform.scale(star_9000_12000_img,(1332, 750))

bored = pg.image.load("./Resources/assets/facial_expressions/bored.png")
angry = pg.image.load("./Resources/assets/facial_expressions/angry.png")
left_confused = pg.image.load("./Resources/assets/facial_expressions/left_confused.png")
right_confused = pg.image.load("./Resources/assets/facial_expressions/right_confused.png")
eyes_closed = pg.image.load("./Resources/assets/facial_expressions/eyes_closed.png")
smile = pg.image.load("./Resources/assets/facial_expressions/smile.png")
wink = pg.image.load("./Resources/assets/facial_expressions/wink.png")
smile_eyes_opened = pg.image.load("./Resources/assets/facial_expressions/smile_eyes_opend.png")

class Emotions:
    def __init__(self, x, y, choice_param : int):
        self.x = x
        self.y = y
        self.choice_param = choice_param

    def render(self):
        # 将变量名从 current_emotion 改为 selected_emotion_img
        # 以明确它是一个图片对象，而不是参数值
        selected_emotion_img = None

        if self.choice_param == 1:
            selected_emotion_img = bored
        elif self.choice_param == 8:
            selected_emotion_img = smile
        elif self.choice_param == 3:
            selected_emotion_img = smile_eyes_opened
        elif self.choice_param == 4:
            selected_emotion_img = angry
        elif self.choice_param == 5:
            selected_emotion_img = left_confused
        elif self.choice_param == 6:
            selected_emotion_img = right_confused
        elif self.choice_param == 2:
            selected_emotion_img = eyes_closed
        elif self.choice_param == 7:
            selected_emotion_img = wink
        else:
            # 添加一个默认值，防止 choice_param 不在预期范围内
            selected_emotion_img = bored  # 或其他默认图片

        # 确保 selected_emotion_img 是图片对象而不是数字
        selected_emotion_img = pg.transform.scale(selected_emotion_img, (200, 200)) #你的图片太！大！了！
        screen.blit(selected_emotion_img, (self.x, self.y))


class Star:
    def __init__(self, x, y, temperature):
        self.x = x
        self.y = y
        self.temperature = temperature
        self.emotion = Emotions(x + 240, y + 50, random.randint(1, 8))

    def render(self):
        selected_star_img = None
        if self.temperature < 5000:
            selected_star_img = star_4000_5000_img
        elif 5000 <= self.temperature < 5500:
            selected_star_img = star_5000_5500_img
        elif 5500 <= self.temperature < 6000:
            selected_star_img = star_5500_6000_img
        elif 6000 <= self.temperature < 7500:
            selected_star_img = star_6000_7500_img
        elif 7500 <= self.temperature < 9000:
            selected_star_img = star_7500_9000_img
        elif 9000 <= self.temperature <= 12000:
            selected_star_img = star_9000_12000_img
        elif self.temperature > 12000:
            selected_star_img = star_9000_12000_img  #或许根本没有这么热的恒星？//确定是没有的，所以我黑体辐射只准备到了12000K，偷个懒哈哈哈
        
        screen.blit(selected_star_img, (self.x, self.y))
        self.emotion.render()



# 创建主菜单按钮
quit_button = Button(650, 665, 300, 50, "退出游戏")#这里就是绘制主菜单的按钮了，几个按钮你就咔咔咔的写
start_engine_button = Button(650, 500, 300, 50, "恒星演化")
sandbox_engine_button = Button(650, 555, 300, 50, "创建宇宙")
credits = Button(650, 610, 300, 50, "制作人员")
background_button_star = Button( 20, 75, 150, 50, "背景切换")
volume_off_button = Button(750,10,200,50,"静音/开音")
bgm_choosing_button = Button(750 ,65,200,50,"切换背景音乐")
engine_mode_button = Button(60, 150, 240, 420,"")
giant_mode_button = Button(360,150,240,420,"")
wd_mode_button = Button(660, 150,240,420,"")
return_button = ReturnButton(20, 20, 150, 50,"返回主菜单")#返回按钮
return_button_bgs = ReturnButton(20, 650, 200, 50, "返回参数界面" )
return_button_in_sim = ReturnButton(20, 20,200,50,"结束演化计算" )
return_button_pattern_choice = ReturnButton(20,20,200,50,"返回主菜单")
background1 = Background_select_button(90,90 , 128, 96, "深蓝星空")
background2 = Background_select_button(230,90 , 128, 96, "纯黑背景")#这是绘制按钮选择界面的按钮
background3 = Background_select_button(370,90 , 128, 96, "乳白银河")
background4 = Background_select_button(510,90 , 128, 96, "黯淡银河")#这是绘制按钮选择界面的按钮
background5 = Background_select_button(650,90 , 128, 96, "深蓝星云")#这是绘制按钮选择界面的按钮
background6 = Background_select_button(90,290 , 128, 96, "星云")#这是绘制按钮选择界面的按钮
background7 = Background_select_button(230,290 , 128, 96, "暗紫银河")#这是绘制按钮选择界面的按钮
background8 = Background_select_button(370,290 , 128, 96, "银河")#这是绘制按钮选择界面的按钮
background9 = Background_select_button(510,290 , 128, 96, "简单星空")#这是绘制按钮选择界面的按钮
# 创建恒星演化界面的按钮
start_simulation_button = Button(180, 540, 200, 50, "开始模拟")
get_recommend_args_button = Button(380, 540, 200, 50, "获取推荐参数")
reset_button = Button(580, 540, 200, 50, "重置参数")
# 创建输入框（带工具提示）
input_boxes = [
    InputBox(500, 160, 200, 40, "恒星质量 (Msun)", 250, "1.0", "范围: 0.8-8.0 太阳质量"),#这里终于想起来给输入框起名字了，感动哭了
    InputBox(500, 240, 200, 40, "金属度 (Z)", 250, "0.02", "范围: 0.001-0.03"),
    InputBox(500, 320, 200, 40, "演化终点 (Myr)", 250, "4540", f"范围: 0.001-恒星寿命的80%（{star.get_tau(1.0, 0.02) * 0.8}）"),
    InputBox(500, 400, 200, 40, "演化步长 (Myr)", 250, "20", "推荐: 主序寿命的0.2%"),
    InputBox(500, 480, 200, 40, "刷新间隔 (秒)", 250, "1", "控制输出速度"),
]

# 定义一下状态文本，还是用户体验这一块，这其实就是一类文字，懒得写class而已
status_text = ""
status_timer = 0
engine_running = False#两个状态，恒星演化开了没开
simulation_running = False  # 标记模拟是否运行

credits_video = VideoFileClip("./Resources/videos/credits.mp4")
credits_video = credits_video.resized((960, 720)) 

# 模拟参数存储
simulation_params = {
    "mass": None ,
    "metallicity": None ,
    "end_time": None ,
    "step_size": None ,
    "refresh_time": None
}

running = True#运行的时候
clock = pg.time.Clock()#应该跟帧率控制有关？

star_instance = Star(160, 180, 0)
last_emotion_second = -1
def play_credits_video(video):
    # 这是一个播放视频的函数
    # 你可以看见它很复杂，而且pygame没有默认api播放视频
    # 所以我用moviepy来处理视频帧，然后用pygame显示
    # 多线程处理视频播放，防止阻塞主线程
    global credits_status, screen, clock
    
    if not credits_status:
        return
    
    event_queue = queue.Queue()
    
    def video_player_thread():
        try:
            fps = video.fps
            if fps <= 0:
                fps = 25 
            
            frame_interval = 1.0 / fps
            frame_count = 0
            
            for frame in video.iter_frames(fps=fps, dtype='uint8'):
                if not credits_status: 
                    break
                
                frame_surface = pg.surfarray.make_surface(
                    np.transpose(frame, (1, 0, 2))
                )
                
                event_queue.put(('frame', frame_surface))
                
                time.sleep(frame_interval)
                frame_count += 1
            
            event_queue.put(('end', None))
            
        except Exception as e:
            print(f"视频播放线程出错: {e}")
            event_queue.put(('error', str(e)))
    
    player_thread = threading.Thread(target=video_player_thread, daemon=True)
    player_thread.start()
    
    while credits_status:
        for event in pg.event.get():
            if event.type == pg.MOUSEBUTTONDOWN:
                credits_status = False
                return
        
        try:
            msg_type, data = event_queue.get(timeout=0.01) 
            if msg_type == 'frame':
                screen.blit(data, (0, 0))
                text_skip = font.render("点击跳过", True, (255, 255, 255))
                screen.blit(text_skip, (0, 0))
                pg.display.flip()
            elif msg_type == 'end':
                credits_status = False
                break
            elif msg_type == 'error':
                print(f"视频播放错误: {data}")
                credits_status = False
                break
        except queue.Empty:
            pass
        
        clock.tick(60) 

while running:
    current_time = pg.time.get_ticks()#定义变量
    mouse_pos = pg.mouse.get_pos()
    current_emotion_second = int(time.time())
    if current_emotion_second != last_emotion_second and current_emotion_second % 2 == 0:
        star_instance.emotion.choice_param = random.randint(1, 2)
        last_emotion_second = current_emotion_second

    #star_instance.emotion.x = star_instance.x + 240 + math.cos(time.time()) * 15
    #star_instance.emotion.y = star_instance.y + 50 + math.sin(time.time()) * 15
    # 只是为了好玩:) 让表情动一动

    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False

        if credits_status:
            play_credits_video(credits_video)
            status_text = "ESC键退出"
            status_timer = current_time + 1500

        # 检查按钮点击
        if not is_in_engine_mode and not is_in_selecting_evo and not evolution_pattern and not simulation_running:
            # 主菜单模式下的按钮点击
            if quit_button.check_click(mouse_pos, event):
                running = False

            elif start_engine_button.check_click(mouse_pos, event):#点了恒星演化以后显示的文字
                # 切换到引擎模式
                evolution_pattern = True
                is_in_selecting_evo = False
                is_in_engine_mode = False
                current_background = selected_background#换背景图在这里！！！！
                status_text = "已进入恒星演化模式"
                status_timer = current_time + 2000#咱得让文字呆一会儿，2s，不能闪现
                simulation_running = False
                # 在主菜单模式下的按钮点击部分，修改静音按钮的逻辑
            # 在主菜单模式下的按钮点击部分，修改静音按钮的逻辑
            elif volume_off_button.check_click(mouse_pos, event):
                if volume_status == False:
                    pg.mixer.music.set_volume(0)
                    volume_status = True
                    status_text = "已静音"
                    status_timer = current_time + 1500
                else:
                    pg.mixer.music.set_volume(1.0)
                    volume_status = False
                    status_text = "已取消静音"
                    status_timer = current_time + 1500
            elif credits.check_click(mouse_pos, event):
                credits_status = True#这里是试图播放的模块，路径./Resources/movies/credits.mp4
            elif bgm_choosing_button.check_click(mouse_pos, event):
                if(music2 == True):
                    pg.mixer.music.load("./Resources/music/Freeze.wav")
                    pg.mixer.music.play(-1)
                    status_text = "已切换至Freeze.wav"
                    status_timer = current_time + 1500
                    music2 = False
                    music3 =True
                elif (music3 == True):
                    pg.mixer.music.load("./Resources/music/SubstituteForSunrise.wav")
                    pg.mixer.music.play(-1)
                    status_text = "已切换至Substitute For Sunrise.wav"
                    status_timer = current_time + 1500
                    music3 = False
                    music1 = True
                elif (music1 == True):
                    pg.mixer.music.load("./Resources/music/infinity.wav")
                    pg.mixer.music.play(-1)
                    status_text = "已切换至infinity.wav"
                    status_timer = current_time + 1500
                    music1 = False
                    music2 = True
        elif evolution_pattern == True and is_in_selecting_evo == False and is_in_engine_mode == False and not simulation_running:
            if engine_mode_button.check_click(mouse_pos, event):
                evolution_pattern = False
                is_in_engine_mode = True
                is_in_selecting_evo = False
                simulation_running = False
            elif return_button_pattern_choice.check_click(mouse_pos, event):
                evolution_pattern = False
                is_in_engine_mode = False
                is_in_selecting_evo = False
                simulation_running = False
                current_background = menu_background



        elif is_in_selecting_evo == False and is_in_engine_mode == True and not simulation_running and not evolution_pattern:
            # 引擎模式下的按钮点击
            if return_button.check_click(mouse_pos, event):
                # 返回主菜单
                is_in_engine_mode = False
                is_in_selecting_evo = False
                current_background = menu_background#换回主菜单背景！
                status_text = "返回主菜单"
                status_timer = current_time + 1500#一样，咱这文字不要闪现
                simulation_running = False
            elif background_button_star.check_click(mouse_pos, event):
                is_in_selecting_evo = True
                is_in_engine_mode = False
                simulation_running = False
                status_text = "进入背景选择模式" if is_in_selecting_evo else "退出背景选择模式"
                status_timer = current_time + 1500
            elif get_recommend_args_button.check_click(mouse_pos, event) and not simulation_running:
                status_text = f"已经获取推荐参数"
                status_timer = current_time + 1500
                tau = star.get_tau(input_boxes[0].get_value(), input_boxes[1].get_value())
                input_boxes[2].text = str(tau * 0.8)
                input_boxes[3].text = str(tau * 0.002)
                input_boxes[2].text_surf = input_font.render(input_boxes[2].text, True, (255, 255, 255))
                input_boxes[3].text_surf = input_font.render(input_boxes[3].text, True, (255, 255, 255))
            elif start_simulation_button.check_click(mouse_pos, event) and not simulation_running:
                is_in_selecting_evo = False
                is_in_engine_mode = False
                simulation_running = True# 你点了开始模拟的按钮而且模拟没开启
                try:
                    # 获取所有参数
                    mass = input_boxes[0].get_value()  # 这里把输入框的数字赋值成物理量
                    metallicity = input_boxes[1].get_value()  # 不然你输入的参数都成了耳旁风了
                    end_time = input_boxes[2].get_value()  # 话说不会真有人看到这里吧？
                    step_size = input_boxes[3].get_value()  # 我操你真看到这里了？！
                    refresh_time = input_boxes[4].get_value()  # 恭喜你，你写程序写的太多了，都刷到我的抱怨了，你TM是第一个（其实也可以是第二个）
                    # 参数验证
                    errors = []  # 你小子有TM乱打字是吧，当我的程序是傻子？和我一样》等等，我好像说了不该说的

                    if mass < 0.799 or mass > 8.001:
                        errors.append("质量需在0.8-8.0Msun之间")
                        simulation_running = False
                        is_in_engine_mode = True

                    if metallicity < 0.0009 or metallicity > 0.0301:
                        errors.append("金属度需在0.001-0.03之间")
                        simulation_running = False
                        is_in_engine_mode = True

                    if end_time <= 0 or end_time > (star.get_tau(mass, metallicity) * 0.8) + 0.001:
                        errors.append(f"演化终点必须大于0且小于恒星寿命的80%（{star.get_tau(mass, metallicity) * 0.8}）")
                        simulation_running = False
                        is_in_engine_mode = True

                    if step_size <= 0:
                        errors.append("演化步长必须大于0")
                        simulation_running = False
                        is_in_engine_mode = True

                    if refresh_time <= 0:
                        errors.append("刷新间隔必须大于0")
                        simulation_running = False
                        is_in_engine_mode = True


                    if errors:
                        status_text = f"参数错误: {'; '.join(errors)}"
                        status_timer = current_time + 4000
                        simulation_running = False
                        is_in_engine_mode = True
                    else:
                        # 保存参数
                        simulation_params = {
                            "mass": mass,
                            "metallicity": metallicity,
                            "end_time": end_time,
                            "step_size": step_size,
                            "refresh_time": refresh_time,
                        }

                        # 启动模拟
                        simulation_running = True
                        status_text = f"开始模拟: M={mass}Msun, Z={metallicity}"
                        status_timer = current_time + 30


                        # 在新线程中运行模拟
                        def run_simulation():  # 这里就是调用恒星演化的引擎了。俗话说的好，拉屎不洗手，亘本.布施仁
                            global simulation_running, status_text, status_timer,simulation_display_data
                            try:
                                if star and hasattr(star, 'mainstar'):
                                    simulation_display_data ={
                                    "age":0.0,
                                    "luminosity":0.0,
                                    "radius":0.0,
                                    "temperature":0.0,
                                    "progress":0.0,
                                    "is_simulating":True,
                                    }
                                    # 调用mainstar函数
                                    star.mainstar(mass=mass, metallicity=metallicity,
                                                  end_time=end_time, step_size=step_size,
                                                  refresh_time=refresh_time)
                                    status_timer = current_time + refresh_time


                                    simulation_running = False
                                    simulation_display_data["is_simulating"] = False
                                else:
                                    status_text = "模拟引擎不可用"
                                    simulation_display_data["is_simulating"] = False
                            except Exception as e:  # 小子你用软件删除物理引擎源代码？被我发现了吧黑嘿潶
                                status_text = f"模拟错误: {str(e)}"
                                print(f"Wrong in simulation: {str(e)}")
                                simulation_display_data["is_simulating"] = False
                            finally:
                                simulation_running = False
                            status_timer = pg.time.get_ticks() + 3000
                            simulation_display_data["is_simulating"] = False
                        is_in_engine_mode = True


                        thread = threading.Thread(target=run_simulation, daemon=True)
                        thread.start()

                except Exception as e:
                    status_text = f"启动失败: {str(e)}"
                    status_timer = current_time + 3000

            elif reset_button.check_click(mouse_pos, event) and not simulation_running and not is_in_selecting_evo and is_in_engine_mode:  # 这里就是你模拟完了一次，咱就需要，诶，重置一下输入框，咱这不是一次性内裤谢谢
                # 重置参数为默认值
                input_boxes[0].text = "1.0"  # 恢复默认值，但这里其实有个bug不太好，每次都要重置
                input_boxes[1].text = "0.02"
                input_boxes[2].text = "4540"
                input_boxes[3].text = "20"
                input_boxes[4].text = "1"

                # 更新文字表面
                for box in input_boxes:
                    box.text_surf = input_font.render(box.text, True, (255, 255, 255))

                simulation_running = False
                status_text = "参数已重置为默认值"
                status_timer = current_time + 2000

                # 处理输入框事件
            if is_in_engine_mode and not simulation_running:
                for box in input_boxes:
                    box.handle_event(event)  # 循环回去

        elif is_in_selecting_evo == True and is_in_engine_mode == False and evolution_pattern == False:
            if return_button.check_click(mouse_pos, event):
                is_in_selecting_evo = False
                is_in_engine_mode = True
                status_text = "返回参数界面"
                status_timer = current_time + 1500
            elif background1.check_click(mouse_pos, event):
                    selected_background = pg.image.load("./Resources/assets/background_files/background_01.jpg")
                    selected_background = pg.transform.scale(selected_background, (960, 720))
                    current_background = selected_background
            elif background2.check_click(mouse_pos, event):
                    selected_background = pg.Surface((960, 720))
                    selected_background.fill((0, 0, 0))
                    current_background = selected_background
            elif background3.check_click(mouse_pos, event):
                    selected_background = pg.image.load("./Resources/assets/background_files/background_03.jpg")
                    selected_background = pg.transform.scale(selected_background, (960, 720))
                    current_background = selected_background
            elif background4.check_click(mouse_pos, event):
                    selected_background = pg.image.load("./Resources/assets/background_files/background_04.jpg")
                    selected_background = pg.transform.scale(selected_background, (960, 720))
                    current_background = selected_background
            elif background5.check_click(mouse_pos, event):
                    selected_background = pg.image.load("./Resources/assets/background_files/background_05.jpg")
                    selected_background = pg.transform.scale(selected_background, (960, 720))
                    current_background =  selected_background
            elif background6.check_click(mouse_pos, event):
                    selected_background = pg.image.load("./Resources/assets/background_files/background_06.jpg")
                    selected_background = pg.transform.scale(selected_background, (960, 720))
                    current_background = selected_background
            elif background7.check_click(mouse_pos, event):
                    selected_background = pg.image.load("./Resources/assets/background_files/background_07.jpg")
                    selected_background = pg.transform.scale(selected_background, (960, 720))
                    current_background = selected_background
            elif background8.check_click(mouse_pos, event):
                    selected_background = pg.image.load("./Resources/assets/background_files/background_08.jpg")
                    selected_background = pg.transform.scale(selected_background, (960, 720))
                    current_background = selected_background
            elif background9.check_click(mouse_pos, event):
                    selected_background = pg.image.load("./Resources/assets/background_files/background_09.jpg")
                    selected_background = pg.transform.scale(selected_background, (960, 720))
                    current_background = selected_background

             # 恒星演化界面的按钮点击

    # 更新按钮悬停状态
    if not is_in_engine_mode and not simulation_running:#你在主菜单，怎么也得处理一下其他的按钮的悬停状态吧
        quit_button.check_hover(mouse_pos)
        credits.check_hover(mouse_pos)
        sandbox_engine_button.check_hover(mouse_pos)
        start_engine_button.check_hover(mouse_pos)
        volume_off_button.check_hover(mouse_pos)
        bgm_choosing_button.check_hover(mouse_pos)
    elif not is_in_engine_mode and not simulation_running and not is_in_selecting_evo and evolution_pattern == True:
        engine_mode_button.check_hover(mouse_pos)
        giant_mode_button.check_hover(mouse_pos)
        wd_mode_button.check_hover(mouse_pos)
    elif is_in_engine_mode and not simulation_running:#这就就是你不在主菜单，就检查界面里的悬停状态
        return_button.check_hover(mouse_pos)
        background_button_star.check_hover(mouse_pos)
        start_simulation_button.check_hover(mouse_pos)
        get_recommend_args_button.check_hover(mouse_pos)
        reset_button.check_hover(mouse_pos)
    elif is_in_selecting_evo and not is_in_engine_mode and not simulation_running:
        background1.check_hover(mouse_pos)
        background2.check_hover(mouse_pos)
        background3.check_hover(mouse_pos)
        background4.check_hover(mouse_pos)
        background5.check_hover(mouse_pos)
        background6.check_hover(mouse_pos)
        background7.check_hover(mouse_pos)
        background8.check_hover(mouse_pos)
        background9.check_hover(mouse_pos)
        return_button_bgs.check_hover(mouse_pos)





    # 绘制背景
    screen.blit(current_background,(0,0))#每次绘制按钮

    if not is_in_engine_mode and not is_in_selecting_evo and not simulation_running and not evolution_pattern:
        # 主菜单界面
        title = title_font.render("行星球宇宙", True, (255, 255, 255))
        subtitle = subtitle_font.render("Universe of PlanetBall", True, (200, 200, 255))

        title_bg = pg.Surface((960, 120), pg.SRCALPHA)
        pg.draw.rect(title_bg, (0, 0, 0, 50), (0, 0, 960, 120))
        screen.blit(title_bg, (0, 0))

        screen.blit(title, (135 - title.get_width() // 2, 20))
        screen.blit(subtitle, (195 - subtitle.get_width() // 2, 80))

        # 绘制按钮
        quit_button.draw(screen)
        start_engine_button.draw(screen)
        sandbox_engine_button.draw(screen)
        credits.draw(screen)
        volume_off_button.draw(screen)
        bgm_choosing_button.draw(screen)

        # 绘制版本信息
        info_texts = [
            "当前版本：Test-V2.1",
            "版本发布日期：预计2026年1月1日",
        ]

        for i, text in enumerate(info_texts):
            info_surf = small_font.render(text, True, (255, 255, 255))
            screen.blit(info_surf, (20, 650 + i * 30))
    elif evolution_pattern == True and not is_in_engine_mode and not is_in_selecting_evo:
     engine_mode_button.draw(screen)
     giant_mode_button.draw(screen)
     wd_mode_button.draw(screen)
     return_button_pattern_choice.draw(screen)
     pattern_title_font = pg.font.Font(None, 50) if font is None else pg.font.Font(
         font_paths[0] if os.path.exists(font_paths[0]) else None, 50)
     pattern_title = pattern_title_font.render("选择演化模块", True, (255, 255, 0))
     screen.blit(pattern_title, (330, 10))
     mainseq_title_font = pg.font.Font(None, 50) if font is None else pg.font.Font(
         font_paths[0] if os.path.exists(font_paths[0]) else None, 30)
     mainseq_title = mainseq_title_font.render("恒星主序演化", True, (100, 255, 100))
     screen.blit(mainseq_title, (90, 525))
     giant_title_font = pg.font.Font(None, 30) if font is None else pg.font.Font(
         font_paths[0] if os.path.exists(font_paths[0]) else None, 30)
     giant_title = giant_title_font.render("敬请期待", True, (255, 100, 100))
     screen.blit(giant_title, (420, 525))
     wd_title_font = pg.font.Font(None, 30) if font is None else pg.font.Font(
         font_paths[0] if os.path.exists(font_paths[0]) else None, 30)
     wd_title = wd_title_font.render("敬请期待", True, (100, 100, 255))
     screen.blit(wd_title, (720, 525))
     main_sequence_tex = pg.image.load("./Resources/assets/button_textures/evolution_evolution.png").convert_alpha()
     pg.transform.scale(main_sequence_tex, (900,675))
     screen.blit(main_sequence_tex, (-150, 150))

    elif is_in_engine_mode==True and is_in_selecting_evo == False and evolution_pattern == False:
        # 恒星演化模式界面
        return_button.draw(screen)

        # 绘制标题
        engine_title_font = pg.font.Font(None, 40) if font is None else pg.font.Font(
            font_paths[0] if os.path.exists(font_paths[0]) else None, 40)
        engine_title = engine_title_font.render("恒星演化引擎", True, (255, 255, 200))

        # 绘制半透明主面板
        main_panel = pg.Surface((600, 500), pg.SRCALPHA)
        pg.draw.rect(main_panel, (0, 0, 0, 100), (0, 0, 600, 500), border_radius=15)
        pg.draw.rect(main_panel, (255, 255, 255, 80), (0, 0, 600, 500), width=3, border_radius=15)
        screen.blit(main_panel, (180, 100))

        # 绘制标题
        screen.blit(engine_title, (480 - engine_title.get_width() // 2, 110))

        # 绘制输入框和工具提示
        for box in input_boxes:
            box.draw(screen)
            box.draw_tooltip(screen, mouse_pos)


        # 绘制按钮
        start_simulation_button.draw(screen)
        get_recommend_args_button.draw(screen)
        reset_button.draw(screen)
        background_button_star.draw(screen)

        # 如果模拟运行中，改变按钮状态
        if simulation_running:
            start_simulation_button.text_surf = font.render("开始模拟", True, (255, 255, 255))
            start_simulation_button.text_rect = start_simulation_button.text_surf.get_rect(
                center=start_simulation_button.rect.center)
            start_simulation_button.current_color = (60, 60, 60, 180)

            # 绘制模拟状态
            status_panel = pg.Surface((600, 150), pg.SRCALPHA)
            pg.draw.rect(status_panel, (0, 20, 40, 180), (0, 0, 400, 150), border_radius=10)
            screen.blit(status_panel, (480 - 300, 620))

            sim_status_font = pg.font.Font(None, 24) if font is None else pg.font.Font(
                font_paths[0] if os.path.exists(font_paths[0]) else None, 24)



            current_background = selected_background
            screen.blit(current_background, (0, 0))
            return_button_in_sim.draw(screen)

            text_time = Text(600, 450, 100, 100, "")
            if star and hasattr(star, 'gt'):
                text_time.set_text(f"年龄: {star.gt:.4f} Myr")
            text_time.render()

            text_light = Text(600, 500, 100, 100, "")
            if star and hasattr(star, 'gL'):
                text_light.set_text(f"光度: {star.gL:.4f} Lsun")
            text_light.render()

            text_radius = Text(600, 550, 100, 100, "")
            if star and hasattr(star, 'gR'):
                text_radius.set_text(f"半径: {star.gR:.4f} Rsun")
            text_radius.render()

            text_temperature = Text(600, 600, 100, 100, "")
            if star and hasattr(star, 'gT'):
                text_temperature.set_text(f"温度: {star.gT:.4f} K")
                star_instance.temperature = star.gT
            text_temperature.render()
            star_instance.render()

            if return_button_in_sim.check_click(mouse_pos,event):
                simulation_running = False
                is_in_engine_mode = True
                is_in_selecting_evo = False
                status_text = "模拟已被手动终止"
                status_timer = current_time + 2000
                if star and hasattr(star, 'stop_mainstar'):
                    star.stop_mainstar = True




    elif is_in_selecting_evo == True and is_in_engine_mode == False:
        screen.blit(current_background, (0, 0))
        overlay = pg.Surface((120, 90), pg.SRCALPHA)
        overlay.fill((0,0,0,100))
        screen.blit(overlay,(0,0))
        background1.draw(screen)
        background2.draw(screen)
        background3.draw(screen)
        background4.draw(screen)
        background5.draw(screen)
        background6.draw(screen)
        background7.draw(screen)
        background8.draw(screen)
        background9.draw(screen)
        return_button_bgs.draw(screen)

    if return_button_bgs.check_click(mouse_pos, event):
            is_in_engine_mode = True
            is_in_selecting_evo = False
    # 绘制状态信息
    if current_time < status_timer:
        status_surf = font.render(status_text, True, (255, 255, 0))
        screen.blit(status_surf, (20, 600))

    # 更新显示
    pg.display.flip()
    clock.tick(60)

pg.quit()