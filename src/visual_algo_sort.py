# visual-algo-sort by fab2112
import numpy as np
import pyqtgraph as pg
import random
import sys
from time import sleep
from PyQt5.QtCore import Qt
from PyQt5 import QtWidgets
from pyqtgraph.Qt import QtCore, QtGui
from multiprocessing import RawArray, RawValue
from multiprocessing import Process


class VisualAlgoSort:
    def __init__(self, data):

        # Object Attributes
        self.data = data
        self.algo_sort = None
        self.start_var = True
        self.delay_value = RawValue('d')
        self.delay_value.value = 50 / 400
        self.finished_value = RawValue('d')
        self.finished_value.value = 0
        self.array_shared_process = RawArray('d', len(self.data))
        self.buffer_array = np.frombuffer(self.array_shared_process)
        np.copyto(self.buffer_array, np.array(self.data))
        self.data2 = np.copy(self.buffer_array)
        self.workProcess = ProcessSort(self.data, self.array_shared_process, self.algo_sort, self.delay_value,
                                       self.finished_value)
        self.timer_plot = QtCore.QTimer()

        # Frame
        self.frame_main = pg.GraphicsLayoutWidget(title="VisualSort - v0.0.0")
        self.frame_main.setGeometry(150, 100, 1400, 900)
        self.plt_1 = self.frame_main.addPlot(row=0, col=1)
        self.plt_1.setTitle('')

        # Config Axis
        self.plt_1.showAxis('right')
        self.plt_1.showAxis('left')
        self.plt_1.showAxis('top')
        self.plt_1.getAxis('left').setStyle(showValues=False)
        self.plt_1.getAxis('right').setStyle(showValues=False)
        self.plt_1.getAxis('top').setStyle(showValues=False)
        self.plt_1.getAxis('bottom').setStyle(showValues=False)

        # Config Frame
        self.plt_1.getAxis('bottom').setPen(pg.mkPen(color='#606060', width=1))
        self.plt_1.getAxis('right').setPen(pg.mkPen(color='#606060', width=1))
        self.plt_1.getAxis('top').setPen(pg.mkPen(color='#606060', width=1))
        self.plt_1.getAxis('left').setPen(pg.mkPen(color='#606060', width=1))

        # Combobox
        self.combobox_1 = QtWidgets.QComboBox(self.frame_main)
        self.combobox_1.setGeometry(120, 10, 90, 25)
        self.combobox_1.addItems(["Bublle", "Insertion", "Quick", "Heap", "Selection", "Radix", "Shell", "Bogo",
                                  "Cocktail", "Bitonic", "Gnome", "Cycle", "Stooge", "OddEven"])
        self.combobox_1.setStyleSheet("font: bold 11pt ;color: white; background-color: #222222; "
                                      "border-radius: 1px; border: 1px solid grey")

        # Slider
        self.slider_1 = QtWidgets.QSlider(self.frame_main)
        self.slider_1.setGeometry(240, 10, 1000, 25)
        self.slider_1.setOrientation(Qt.Horizontal)
        self.slider_1.setMinimum(0)
        self.slider_1.setMaximum(10000)
        self.slider_1.setSliderPosition(5000)
        self.slider_1.valueChanged[int].connect(self.qslider_value)
        self.slider_1.setStyleSheet("QSlider::hover {background: #FF5A5A5A;}")

        # Start/Stop Button
        self.button_1 = QtWidgets.QPushButton(self.frame_main)
        self.button_1.clicked.connect(self.start_sorting)
        self.button_1.setGeometry(10, 10, 80, 25)
        self.button_1.setText('START')
        self.button_1.show()
        self.button_1.setStyleSheet("font: bold 11pt ;color: white; background-color: #228B22; "
                                    "border-radius: 1px; border: 1px solid grey")

        # Delay TextItem
        self.delay_textitem = pg.TextItem(color='white')
        self.delay_textitem.setParentItem(self.plt_1)
        self.delay_textitem.setPos(1250, 0)
        self.delay_textitem.setText(text="Delay: {} ms     ".format(round(round(self.delay_value.value, 4) * 100, 3)))

        self.frame_main.show()

    def qslider_value(self, value):
        self.delay_value.value = value / 40000
        text = "Delay: {} ms     ".format(round(round(self.delay_value.value, 4) * 100, 3))
        self.delay_textitem.setText(text=text)

    def start_plot(self):

        def update():

            if self.finished_value.value == 0:
                indexbg2 = np.where(self.buffer_array != self.data2)[0]
                rndcolor = random.randint(0, 255)
                bargraph1 = pg.BarGraphItem(x=range(len(self.data)), height=self.buffer_array, width=1,
                                            brush='#D3D3D3', pen='#D3D3D3')
                bargraph2 = pg.BarGraphItem(x=indexbg2, height=np.take(self.buffer_array, indexbg2),
                                            width=1, brush=rndcolor, pen=rndcolor)
                if sum(np.take(self.buffer_array, indexbg2)) != 0:
                    self.plt_1.clear()
                    self.plt_1.addItem(bargraph1)
                    self.plt_1.addItem(bargraph2)
                    self.data2 = np.copy(self.buffer_array)

                if self.start_var:
                    self.plt_1.clear()
                    self.plt_1.addItem(bargraph1)

            elif self.finished_value.value == 1:
                self.plt_1.clear()
                bargraph1 = pg.BarGraphItem(x=range(len(self.data)), height=self.buffer_array, width=1,
                                            brush='#5F9EA0', pen='#5F9EA0')
                self.plt_1.addItem(bargraph1)

            else:
                self.plt_1.clear()
                bargraph1 = pg.BarGraphItem(x=range(len(self.data)), height=self.buffer_array, width=1,
                                            brush='r', pen='r')
                self.plt_1.addItem(bargraph1)

        self.timer_plot.timeout.connect(update)
        self.timer_plot.start()

        if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
            QtWidgets.QApplication.instance().exec_()

    def start_sorting(self):

        if self.start_var:
            self.algo_sort = self.combobox_1.currentText()
            self.workProcess = ProcessSort(self.data, self.array_shared_process, self.algo_sort, self.delay_value,
                                           self.finished_value)
            self.workProcess.start()
            self.start_var = False
            self.button_1.setText('STOP')
            self.button_1.setStyleSheet("font: bold 11pt ;color: white; background-color: #B22222; "
                                        "border-radius: 1px; border: 1px solid grey")
        else:
            self.workProcess.terminate()
            self.workProcess.join()
            np.copyto(self.buffer_array, np.array(self.data))
            self.start_var = True
            self.finished_value.value = 0
            self.button_1.setText('START')
            self.button_1.setStyleSheet("font: bold 11pt ;color: white; background-color: #228B22; "
                                        "border-radius: 1px; border: 1px solid grey")


class ProcessSort(Process):
    def __init__(self, data, array_shared_process, algo_sort, delay, finished):
        Process.__init__(self)
        self.data = data
        self.array_shared_process = array_shared_process
        self.buffer_array = np.frombuffer(self.array_shared_process)
        self.algo_sort = algo_sort
        self.delay = delay
        self.finished_value = finished

    def run(self):
        try:
            if self.algo_sort == 'Bublle':
                self.bubble_sort(self.data)
            elif self.algo_sort == 'Insertion':
                self.insertion_sort(self.data)
            elif self.algo_sort == 'Quick':
                self.quick_sort(self.data, 0, len(data) - 1)
            elif self.algo_sort == 'Heap':
                self.heap_sort(self.data)
            elif self.algo_sort == 'Selection':
                self.selection_sort(self.data, len(data))
            elif self.algo_sort == 'Radix':
                self.radix_sort(self.data)
            elif self.algo_sort == 'Shell':
                self.shell_sort(self.data, len(data))
            elif self.algo_sort == 'Bogo':
                self.bogo_sort(self.data)
            elif self.algo_sort == 'Cocktail':
                self.cocktail_sort(self.data)
            elif self.algo_sort == 'Bitonic':
                self.bitonic_sort(self.data, 0, len(self.data), 1)
            elif self.algo_sort == 'Gnome':
                self.gnome_sort(self.data, len(self.data))
            elif self.algo_sort == 'Cycle':
                self.cycle_sort(self.data)
            elif self.algo_sort == 'Stooge':
                self.stooge_sort(self.data, 0, len(self.data) - 1)
            elif self.algo_sort == 'OddEven':
                self.oddeven_sort(self.data, len(data))

            self.finished_value.value = 1

        except:
            print("FAIL!!!")
            self.finished_value.value = 2
            # raise sys.exc_info()[0]

    # Bubble-Sort
    def bubble_sort(self, array):
        for i in range(len(array) - 1):
            for j in range(len(array) - i - 1):
                if array[j] > array[j + 1]:
                    array[j], array[j + 1] = array[j + 1], array[j]
                    sleep(self.delay.value)
                    np.copyto(self.buffer_array, np.array(array))

    # Insertion-Sort
    def insertion_sort(self, array):
        for i in range(1, len(array)):
            x = array[i]
            j = i - 1
            while j >= 0 and x < array[j]:
                array[j + 1] = array[j]
                j -= 1
                sleep(self.delay.value)
                np.copyto(self.buffer_array, np.array(array))
            array[j + 1] = x
            sleep(self.delay.value)
            np.copyto(self.buffer_array, np.array(array))

    # Quick-Sort
    def partition_quick(self, array, low, high):
        pivot = array[high]
        i = low - 1
        for j in range(low, high):
            if array[j] <= pivot:
                i = i + 1
                (array[i], array[j]) = (array[j], array[i])
                sleep(self.delay.value)
                np.copyto(self.buffer_array, np.array(array))
        (array[i + 1], array[high]) = (array[high], array[i + 1])
        sleep(self.delay.value)
        np.copyto(self.buffer_array, np.array(array))

        return i + 1

    def quick_sort(self, array, low, high):
        if low < high:
            sleep(self.delay.value)
            np.copyto(self.buffer_array, np.array(array))
            pi = self.partition_quick(array, low, high)
            self.quick_sort(array, low, pi - 1)
            self.quick_sort(array, pi + 1, high)
            sleep(self.delay.value)
            np.copyto(self.buffer_array, np.array(array))

    # Heap-Sort
    def heapify(self, array, n, i):
        largest = i
        left = 2 * i + 1
        right = 2 * i + 2
        if left < n and array[i] < array[left]:
            largest = left
        if right < n and array[largest] < array[right]:
            largest = right
        if largest != i:
            array[i], array[largest] = array[largest], array[i]
            self.heapify(array, n, largest)
        sleep(self.delay.value)
        np.copyto(self.buffer_array, np.array(array))

    def heap_sort(self, array):
        n = len(array)
        for i in range(n // 2, -1, -1):
            self.heapify(array, n, i)
        for i in range(n - 1, 0, -1):
            array[i], array[0] = array[0], array[i]
            self.heapify(array, i, 0)
        return array

    # Selection-Sort
    def selection_sort(self, array, size):
        for step in range(size):
            min_idx = step
            for i in range(step + 1, size):
                if array[i] < array[min_idx]:
                    min_idx = i
                sleep(self.delay.value)
                np.copyto(self.buffer_array, np.array(array))
            (array[step], array[min_idx]) = (array[min_idx], array[step])
            sleep(self.delay.value)
            np.copyto(self.buffer_array, np.array(array))

    # Radix-Sort
    def counting_radix(self, array, place):
        size = len(array)
        output = [0] * size
        count = [0] * 10
        for i in range(0, size):
            index = array[i] // place
            count[index % 10] += 1
        for i in range(1, 10):
            count[i] += count[i - 1]
        i = size - 1
        while i >= 0:
            index = array[i] // place
            output[count[index % 10] - 1] = array[i]
            count[index % 10] -= 1
            i -= 1
        for i in range(0, size):
            array[i] = output[i]
            sleep(self.delay.value)
            np.copyto(self.buffer_array, np.array(array))

    def radix_sort(self, array):
        max_element = max(array)
        place = 1
        while max_element // place > 0:
            self.counting_radix(array, place)
            place *= 10
            sleep(self.delay.value)
            np.copyto(self.buffer_array, np.array(array))

    # Shell-Sort
    def shell_sort(self, array, n):
        interval = n // 2
        while interval > 0:
            for i in range(interval, n):
                temp = array[i]
                j = i
                while j >= interval and array[j - interval] > temp:
                    array[j] = array[j - interval]
                    j -= interval
                    sleep(self.delay.value)
                    np.copyto(self.buffer_array, np.array(array))
                array[j] = temp
            interval //= 2
            sleep(self.delay.value)
            np.copyto(self.buffer_array, np.array(array))

    # Bogo-Sort
    def bogo_sort(self, array):
        while self.is_sorted_bogo(array) is False:
            self.shuffle_bogo(array)
            sleep(self.delay.value)
            np.copyto(self.buffer_array, np.array(array))

    @staticmethod
    def is_sorted_bogo(array):
        n = len(array)
        for i in range(0, n - 1):
            if array[i] > array[i + 1]:
                return False
        return True

    @staticmethod
    def shuffle_bogo(array):
        n = len(array)
        for i in range(0, n):
            r = random.randint(0, n - 1)
            array[i], array[r] = array[r], array[i]

    # Cocktail-Sort
    def cocktail_sort(self, array):
        n = len(array)
        swapped = True
        start = 0
        end = n - 1
        while swapped is True:
            swapped = False
            for i in range(start, end):
                if array[i] > array[i + 1]:
                    array[i], array[i + 1] = array[i + 1], array[i]
                    swapped = True
                sleep(self.delay.value)
                np.copyto(self.buffer_array, np.array(array))
            if swapped is False:
                break
            swapped = False
            end = end - 1
            for i in range(end - 1, start - 1, -1):
                if array[i] > array[i + 1]:
                    array[i], array[i + 1] = array[i + 1], array[i]
                    swapped = True
                sleep(self.delay.value)
                np.copyto(self.buffer_array, np.array(array))
            start = start + 1

    # Bitonic-Sort
    @staticmethod
    def compare_swap_bitonic(array, i, j, d):
        if (d == 1 and array[i] > array[j]) or (d == 0 and array[i] < array[j]):
            array[i], array[j] = array[j], array[i]

    def merge_bitonic(self, array, l, cnt, d):
        if cnt > 1:
            k = int(cnt / 2)
            for i in range(l, l + k):
                self.compare_swap_bitonic(array, i, i + k, d)
                sleep(self.delay.value)
                np.copyto(self.buffer_array, np.array(array))
            self.merge_bitonic(array, l, k, d)
            self.merge_bitonic(array, l + k, k, d)
        sleep(self.delay.value)
        np.copyto(self.buffer_array, np.array(array))

    def bitonic_sort(self, array, l, cnt, d):
        if cnt > 1:
            k = int(cnt / 2)
            self.bitonic_sort(array, l, k, 1)
            sleep(self.delay.value)
            np.copyto(self.buffer_array, np.array(array))
            self.bitonic_sort(array, l + k, k, 0)
            self.merge_bitonic(array, l, cnt, d)
        sleep(self.delay.value)
        np.copyto(self.buffer_array, np.array(array))

    # Gnome-Sort
    def gnome_sort(self, array, n):
        index = 0
        while index < n:
            if index == 0:
                index = index + 1
            if array[index] >= array[index - 1]:
                index = index + 1
            else:
                array[index], array[index - 1] = array[index - 1], array[index]
                index = index - 1
            sleep(self.delay.value)
            np.copyto(self.buffer_array, np.array(array))

    # Circle-Sort
    def cycle_sort(self, array):
        write = 0
        for cycle in range(0, len(array) - 1):
            ele = array[cycle]
            position = cycle
            for i in range(cycle + 1, len(array)):
                if array[i] < ele:
                    position += 1
            if position == cycle:
                continue
            while ele == array[position]:
                position += 1
            array[position], ele = ele, array[position]
            write += 1
            sleep(self.delay.value)
            np.copyto(self.buffer_array, np.array(array))
            while position != cycle:
                position = cycle
                for a in range(cycle + 1, len(array)):
                    if array[a] < ele:
                        position += 1
                while ele == array[position]:
                    position += 1
                array[position], ele = ele, array[position]
                write += 1
                sleep(self.delay.value)
                np.copyto(self.buffer_array, np.array(array))

    # Stooge-Sort
    def stooge_sort(self, array, l, h):
        sleep(self.delay.value)
        np.copyto(self.buffer_array, np.array(array))
        if l >= h:
            return
        if array[l] > array[h]:
            t = array[l]
            array[l] = array[h]
            array[h] = t
            sleep(self.delay.value)
            np.copyto(self.buffer_array, np.array(array))
        if h - l + 1 > 2:
            t = int((h - l + 1) / 3)
            self.stooge_sort(array, l, (h - t))
            self.stooge_sort(array, l + t, (h))
            self.stooge_sort(array, l, (h - t))

    # OddEven-Sort
    def oddeven_sort(self, array, n):
        issorted = 0
        while issorted == 0:
            issorted = 1
            for i in range(1, n - 1, 2):
                if array[i] > array[i + 1]:
                    array[i], array[i + 1] = array[i + 1], array[i]
                    issorted = 0
                sleep(self.delay.value)
                np.copyto(self.buffer_array, np.array(array))
            for i in range(0, n - 1, 2):
                if array[i] > array[i + 1]:
                    array[i], array[i + 1] = array[i + 1], array[i]
                    issorted = 0
                sleep(self.delay.value)
                np.copyto(self.buffer_array, np.array(array))


# Random int
#data = random.sample(range(0, 256), 256)

# Random float
#data = 10 * np.random.random_sample(size=1000)

# Gaussian
data = np.random.normal(size=(256,))

# Random walking
#data = np.exp(np.cumsum(0.03 * np.random.standard_normal(size=(256,))))

# Reversed
#data = np.array(range(256)[::-1])


sort = VisualAlgoSort(data)
sort.start_plot()
