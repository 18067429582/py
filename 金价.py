import tk as tk
import tkinter as tk
import requests
import threading
import time


class GoldDesktopWidget:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("实时金价")

        # 窗口设置：置顶、无边框
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)
        self.root.geometry("200x90+100+100")
        self.root.config(bg="#1c1c1c")  # 深色背景

        # UI 布局
        self.label_title = tk.Label(self.root, text="实时金价行情 (右键退出)", font=("微软雅黑", 8), fg="#7f8c8d",
                                    bg="#1c1c1c")
        self.label_title.pack(pady=2)

        self.label_cn = tk.Label(self.root, text="沪金: --", font=("微软雅黑", 14, "bold"), fg="white", bg="#1c1c1c")
        self.label_cn.pack()

        self.label_int = tk.Label(self.root, text="伦敦金: --", font=("微软雅黑", 11), fg="#ecf0f1", bg="#1c1c1c")
        self.label_int.pack()

        # 鼠标左键拖动，右键退出
        self.root.bind("<Button-1>", self.save_pos)
        self.root.bind("<B1-Motion>", self.move_window)
        self.root.bind("<Button-3>", lambda e: self.root.quit())

        # 启动数据更新线程
        threading.Thread(target=self.refresh_logic, daemon=True).start()

    def save_pos(self, event):
        self.offset_x = event.x
        self.offset_y = event.y

    def move_window(self, event):
        x = self.root.winfo_x() + (event.x - self.offset_x)
        y = self.root.winfo_y() + (event.y - self.offset_y)
        self.root.geometry(f"+{x}+{y}")

    def fetch_data(self):
        headers = {
            "Referer": "https://finance.sina.com.cn",
            "User-Agent": "Mozilla/5.0"
        }
        try:
            url = "https://hq.sinajs.cn/list=gds_AU9999,hf_XAU"
            response = requests.get(url, headers=headers, timeout=5)
            content = response.content.decode('gbk')
            lines = content.split('\n')

            # 解析国内金 (Au9999) -> [最新价, 昨收价]
            cn_data = lines[0].split('"')[1].split(',')
            cn_now, cn_last = cn_data[0], cn_data[3]

            # 解析国际金 (XAU) -> [最新价, 昨收价]
            int_data = lines[1].split('"')[1].split(',')
            int_now, int_last = int_data[0], int_data[7]

            return (float(cn_now), float(cn_last)), (float(int_now), float(int_last))
        except Exception as e:
            print(f"API获取失败: {e}")
            return None, None

    def refresh_logic(self):
        while True:
            cn, inter = self.fetch_data()
            if cn and inter:
                # 国内涨跌颜色逻辑
                cn_color = "#e74c3c" if cn[0] >= cn[1] else "#2ecc71"  # 红涨绿跌
                self.label_cn.config(text=f"沪金: ¥{cn[0]:.2f}", fg=cn_color)

                # 国际涨跌颜色逻辑
                int_color = "#e74c3c" if inter[0] >= inter[1] else "#2ecc71"
                self.label_int.config(text=f"伦敦金: ${inter[0]:.2f}", fg=int_color)

            time.sleep(1)  # 10秒刷新一次

    def start(self):
        # 修复点：调用 tkinter 的主循环
        self.root.mainloop()


if __name__ == "__main__":
    app = GoldDesktopWidget()
    app.start()  # 这里的名字要和定义的函数名一致