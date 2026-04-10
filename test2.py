import math
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import time

# 初始化圖形
fig, ax = plt.subplots()
xdata, ydata = [], []
line, = ax.plot([], [], lw=2)

# 設置圖表範圍
ax.set_xlim(0, 10)
ax.set_ylim(-1.5, 1.5)

# 獲取開始時間
start_time = time.time()

# 初始化數據
def init():
    line.set_data([], [])
    return line,

# 動畫更新函數
def update(frame):
    for _ in range(10):  # 每次更新添加 10 個數據點
        current_time = time.time() - start_time
        xdata.append(current_time)
        ydata.append(math.sin(current_time))
        

    
    # 只保留最近的 10 秒數據
    if current_time > 10:
        ax.set_xlim(current_time - 10, current_time)
        xdata.pop(0)
        ydata.pop(0)

    line.set_data(xdata, ydata)
    return line,

plt.show()
