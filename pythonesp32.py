import sys
import serial
import time
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel
from PyQt5.QtGui import QFont
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.animation as animation
import warnings
warnings.filterwarnings("ignore", message="frames=None which we can infer the length of, did not pass an explicit *save_count* and passed cache_frame_data=True")


class MplCanvas(FigureCanvas):
    def __init__(self, parent=None, width=8, height=6, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.ax = self.fig.add_subplot(1, 1, 1)
        
        # 设置子图标题和坐标轴标签
        self.ax.set_title('ECG')
        self.ax.set_xlabel('Time')
        self.ax.set_ylabel('Voltage')
        self.ax.set_ylim(0, 2)
        
        super(MplCanvas, self).__init__(self.fig)

class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        # 创建一个Matplotlib画布
        self.canvas = MplCanvas(self)
        
        # 创建三个显示数值的标签
        self.label_spo2 = QLabel('SPO2: --')
        self.label_emg = QLabel('EMG: --')
        self.label_hr = QLabel('HR: --')

        # 设置标签字体大小
        font = QFont()
        font.setPointSize(14)  # 设置字体大小为14
        self.label_spo2.setFont(font)
        self.label_emg.setFont(font)
        self.label_hr.setFont(font)

        # 创建一个垂直布局管理器
        layout = QVBoxLayout()
        layout.addWidget(self.label_spo2)
        layout.addWidget(self.label_emg)
        layout.addWidget(self.label_hr)
        layout.addWidget(self.canvas)

        # 创建一个主Widget并设置布局
        main_widget = QWidget()
        main_widget.setLayout(layout)
        self.setCentralWidget(main_widget)

        # 串口初始化
        self.port = 'COM5'  # 根据您的实际情况设置
        self.baudrate = 9600
        try:
            self.ser = serial.Serial(self.port, self.baudrate)
        except serial.SerialException as e:
            print(f"Could not open port {self.port}: {e}")
            exit()

        self.xdata, self.ydata = [], []
        self.line, = self.canvas.ax.plot(self.xdata, self.ydata, lw=2)

        # 获取开始时间
        self.start_time = time.time()

        # 设置动画
        self.ani = animation.FuncAnimation(self.canvas.fig, self.update, blit=False,interval=10, cache_frame_data=False)

    def update(self, frame):
        current_time = time.time() - self.start_time
        try:
            data = self.ser.readline().decode('utf-8')   
            #print(f"data:{data}")         
            data=data.split("@")   
            #print(f"Received: {data[3]}")  # 打印接收到的数据以确认格式
            ecg_value = float(data[3])  # 仅使用索引为3的数据作为ECG值

            self.ydata.append(ecg_value)
            self.xdata.append(current_time)
            if current_time > 10:
                self.canvas.ax.set_xlim(current_time - 10, current_time)
                self.xdata.pop(0)
                self.ydata.pop(0)
            self.line.set_data(self.xdata, self.ydata)
            self.canvas.ax.relim()
            self.canvas.ax.autoscale_view()

            # 更新显示数值的标签
            self.label_spo2.setText(f'SPO2: {data[0]}')
            self.label_emg.setText(f'EMG: {data[2]}')
            self.label_hr.setText(f'HR: {data[1]}')

        except Exception as e:
            print(f"Error: {e}")
        return self.line,

    def closeEvent(self, event):
        self.ser.close()
        event.accept()

app = QApplication(sys.argv)
w = MainWindow()
w.show()
app.exec_()
