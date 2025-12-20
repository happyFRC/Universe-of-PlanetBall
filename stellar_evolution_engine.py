import time
import math
from xml.dom.minidom import ProcessingInstruction

from pkg_resources import require

global stop_mainstar
global current_simulation_data
global gt, gT, gL, gR
stop_mainstar = False
gt, gT, gL, gR = 0.0, 0.0, 0.0, 0.0


def get_tau(mass=None, metallicity=None):
    if mass is None or metallicity is None:
        return None
    if mass >= 0.799 and mass <= 2.0:
        tau_base = math.pow(mass, -3) * 10000
    elif mass > 2.0 and mass <= 3.33:
        tau_base = math.pow(mass, -3) * (0.3 * mass / 0.6) * 10000
    elif mass > 3.33 and mass < 8.001:
        tau_base = math.pow(mass, -3) * (5.0 / 3.0) * 10000
    else:
        return 0 # TODO: 补全
    return math.pow((metallicity / 0.02), 0.19953) * tau_base

def mainstar(mass=None, metallicity=None, end_time=None, step_size=None, refresh_time=None):
    """
    恒星演化主函数
    参数：
    mass: 恒星质量(0.8-1.6Msun)，默认为None（使用交互式输入）
    metallicity: 金属度(0.001-0.03)
    end_time: 演化终点(Myr)
    step_size: 演化步长(Myr)
    refresh_time: 刷新时间(秒)
    """
    global stop_mainstar

    # 检查是否使用参数模式
    required_params = [mass, metallicity, end_time, step_size, refresh_time]
    use_params = all(param is not None for param in required_params)

    if not use_params:
        # 交互式模式 - 原来的代码
        notice = 0
        print("欢迎来到行星球宇宙！")
        print("当前版本：测试-V1.2 更新日期：2025年12月6日")
        print("要查看更新内容吗(按'1'查看'2'直接使用）?")

        try:
            notice = int(input())
        except ValueError:
            notice = 2

        if notice == 1:
            print("更新内容：")
            print("1：更新了基于金属度的主序星寿命,拟合参数的计算机制")
            print("2：修复了步长分配系统的bug")
            print("3：缩短了计算范围，为了避免主序后期亮度偏差过高")
            print("4：修正了输入边界金属度误判为输入无效的问题")

    while True:
        #变量声明
        M = L = Mc = z = t = dt = XHc = XHec = mu = Tc = Tb = k = tend = pp = cno = 0.0
        mu0 = Tc0 = Msun = c = cno0 = pp0 = XH0 = XHe0 = delta_mass = n = tau = recommend = half = tau_r = 0.0
        R = R0 = T = 0.0
        factor = 0.0  # V1.1新增内容!
        tau_base = critical = 0.0  # V1.2新增内容!

        c = 299792458.0
        XHc = 0.5697
        XHec = 0.4303
        mu = 0.6839
        Tb = 18000000.0
        Msun = math.pow(10, 30) * 2

        if not use_params:
            print("\n版本test-V1.2")
            print("提示：")
            print("请按照规定内容输入，只用输入纯数字")
            print("刷新时间是指输出下一步长后的数据前的间隔时间")
            print("如果你需要计算到主序星寿命一半以后的参数，建议调高时间步长，可以获得更精确的结果。")
            print(
                "本算法采用数值积分算法，对时间步长很敏感，对于计算到主序星寿命一半及以下的恒星，推荐演化步长为主序寿命的0.2%")
            print("超过主序寿命一半的，系统自动分配步长")

        # 获取恒星质量
        if use_params:
            M = mass
        else:
            while True:
                print("请输入恒星质量(0.8-8.0Msun):")
                try:
                    M = float(input())
                    if M < 0.799 or M > 8.001:
                        print("输入无效！请重新输入！")
                        continue
                    break
                except ValueError:
                    print("输入无效！请重新输入！")

        # 获取金属度
        if use_params:
            z = metallicity
        else:
            while True:
                print("请输入金属度（0.001-0.03）:")
                try:
                    z = float(input())
                    if z < 0.0009 or z > 0.0301:
                        print("输入无效！请重新输入！")
                        continue
                    break
                except ValueError:
                    print("输入无效！请重新输入！")

        # 计算参数
        factor = math.pow((z / 0.02), (-0.025))
        if(M>=0.799 and M<=2.0):
            L = math.pow(M, 4.65) * (0.6 + math.pow(1.85, (-200 * z)))
        elif(M>2.0 and M<8.001):
            L=(math.pow(M,4.2)+6.73)*(0.6+math.pow(1.85, (-200 * z)))
        L0=L
        if(M>0.799 and M<=2.0):
            tau_base = math.pow(M, -3) * 10000
        elif(M>2.0 and M<=3.33):
            tau_base = math.pow(M, -3) *(0.3*M/0.6) * 10000
        elif(M>3.33 and M<8.001):
            tau_base = math.pow(M, -3) * (5.0/3.0) * 10000
        tau = math.pow((z / 0.02), 0.19953) * tau_base
        recommend = 0.002 * tau
        half = 0.5 * tau
        critical = 0.8 * tau

        if not use_params:
            print(f"参考：该恒星的预估主序寿命(Myr)：{tau}")
            print(f"推荐步长：{recommend}")
            print(f"主序过半界限：{half}")
            print(f"支持最大输入：{critical}")

        # 获取演化终点
        if use_params:
            tend = end_time
        else:
            while True:
                print("请输入演化终点(Myr)（不建议超过恒星主序寿命的80%）")
                try:
                    tend = float(input())
                    if tend < 0 or tend > 0.8 * tau:
                        print("输入无效！请重新输入！")
                        continue
                    break
                except ValueError:
                    print("输入无效！请重新输入！")

        # 获取演化步长
        if use_params:
            dt = step_size
        elif tend <= half:
            while True:
                print("请输入演化步长（百万年):")
                try:
                    dt = float(input())
                    break
                except ValueError:
                    print("输入无效！请重新输入！")
        else:  # tend > half
            dt = math.pow((tend / half), 4) * (0.002 * math.pow(M, -3) * 10000)
            if not use_params:
                print("恭喜你，超出一半了，系统已为你自动分配对应的步长，痛失步长自主权")

        # 获取刷新时间
        if use_params:
            n = refresh_time
        else:
            while True:
                print("请输入刷新时间（秒）")
                try:
                    n = float(input())
                    break
                except ValueError:
                    print("输入无效！请重新输入！")

        # 初始化计算
        R0 = 0.9 * math.pow(M, 0.9) * factor
        R = R0
        Mc = math.pow(M, 0.6) * 0.57
        if(M>0.799 and M<=1.6):
            k = ((85000.0) / (12160.0) * z + 0.860197) * (-0.71 * M + 1.435)
        elif(M>1.6 and M<=2.0):
            k=((85000.0/12160.0)*z+0.860197)*(-0.4475*M+1.015)
        elif(M>2.0 and M<=3.0):
            k= (-1.0 / 60.0) * M + (4.6 / 30.0) * ((85000 / 12160) * z + 0.860197)
        elif(M>3.0 and M<=4.5):
            k= (((-0.02)*M)+0.14)*((85000.0/12160.0)*z+0.860197)
        elif(M>4.5 and M<=8.0):
            k=(((-0.01)*M)+0.1)*((85000.0 / 12160.0) * z + 0.860197)
        Tc = 15000000 * math.pow(M, 0.34)
        T = math.pow((L / math.pow(R, 2)), 0.25) * 5773.15
        pp = math.pow((Tc / Tb), 5) / (math.pow((Tc / Tb), 5) + math.pow((Tc / Tb), 15)) * L
        cno = L - pp

        print("年龄(Myr)\t光度(Lsun)\t半径（Rsun）\t表面温度（K）")

        # 主循环计算
        t = 0.0
        while t <= tend:
            if stop_mainstar:
                stop_mainstar = False
                break

            print(f"{t:.6f}\t{L:.6f}\t{R:.6f}\t{T:.6f}")
            global gt, gT, gL, gR
            gt = t
            gT = T
            gL = L
            gR = R

            XH0 = XHc
            XHe0 = XHec
            delta_mass = 200 * (L * 3.83e26) * (dt * 1e6 * 365.24 * 86400) / (c * c)
            XHc = (Mc * Msun * XH0 - delta_mass) / (Mc * Msun)
            XHec = 1.0 - XHc
            mu0 = mu
            mu = 1 / (2 * XHc + 0.75 * XHec)
            Tc0 = Tc
            Tc = (0.95 * k * ((mu - mu0) / mu0) + 1) * Tc0
            pp0 = pp
            cno0 = cno
            L0 = L
            L = pp0 * math.pow((Tc / Tc0), 5) + cno0 * math.pow((Tc / Tc0), 15)
            pp = pp0 * math.pow((Tc / Tc0), 5)
            cno = cno0 * math.pow((Tc / Tc0), 15)  # 计算光度
            tau_r = ((t + dt) / tau)
            R = R *math.pow((L/L0),0.28)
            T = math.pow((L / math.pow(R, 2)), 0.25) * 5773.15
            data_texts = [
                f"当前年龄: {t} Myr",
                f"恒星光度: {L} L☉",
                f"恒星半径: {R} R☉",
                f"表面温度: {T} K",
                f"模拟进度: {t/end_time*100}%"
            ]





            # 休眠
            time.sleep(n)

            t = t + dt


        print("\n计算完成！")

        if not use_params:
            # 询问是否重新开始
            print("\n是否重新开始新的计算？")
            print("1. 是，重新开始计算")
            print("2. 否，退出程序")
            print("请选择（1或2）: ")

            try:
                restart = int(input())
                if restart != 1:
                    print("\n程序结束。")
                    break  # 退出while循环
            except ValueError:
                print("\n程序结束。")
                break
        elif use_params:
            break




if __name__ == "__main__":
    # 两种使用方式：
    # 1. 交互式模式（不传参数）
    # mainstar()

    # 2. 参数模式（示例）
    # mainstar(mass=1.0, metallicity=0.02, end_time=5000, step_size=10, refresh_time=0.5)

    mainstar()