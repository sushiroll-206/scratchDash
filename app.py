import sys
import os
import threading
import psutil
import matplotlib.pyplot as plt
from io import BytesIO
from collections import deque

from time import strftime, sleep, localtime

from PyQt6.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import QTimer, pyqtSignal, QObject
from matplotlib.figure import Figure




class Backend(QObject):

    def __init__(self):
        QObject.__init__(self)
        self.cpu_history = deque([0]*60, maxlen=60)

    updated = pyqtSignal(float, list, arguments=['updater', 'cpu_history'])

    def bootUp(self):
        t_thread = threading.Thread(target=self._bootUp)
        t_thread.daemon = True
        t_thread.start()

    def _bootUp(self):
        while True:
            cpu_usage = psutil.cpu_percent(interval=1)

            self.cpu_history.append(cpu_usage)

            self.updater(cpu_usage, self.cpu_history)
            sleep(0.1)
    
    def updater(self, cpu_usage, cpu_history):
        self.updated.emit(cpu_usage, cpu_history)


class MainWindow(QWidget):
    def __init__(self, backend):
        super().__init__()

        self.backend = backend
        self.initUI()

        # Connect the backend signal to update the UI
        self.backend.updated.connect(self.updateUI)

        # Start fetching CPU usage data
        self.backend.bootUp()

    def initUI(self):
        self.setWindowTitle("CPU Usage Graph")
        self.setGeometry(100, 100, 800, 600)

        # Create a QLabel to display the graph
        self.graph_label = QLabel(self)
        
        # Create a label to display the current CPU usage
        self.cpu_label = QLabel(self)
        self.cpu_label.setText("CPU Usage: 0%")

        # Set up the layout
        layout = QVBoxLayout()
        layout.addWidget(self.cpu_label)
        layout.addWidget(self.graph_label)
        self.setLayout(layout)

    def updateUI(self, cpu_usage, history):
        # Generate the graph and display it
        pixmap = self.generateGraph(history, cpu_usage)
        self.graph_label.setPixmap(pixmap)

    def generateGraph(self, history, cpu_usage):
        # Create a matplotlib figure and axis
        fig = Figure(figsize=(8, 4))
        ax = fig.add_subplot(111)

        print(history)

        fig.patch.set_facecolor('darkgray')
        ax.set_facecolor('darkgray')

        # Remove the x-axis labels (sliding window effect)
        ax.set_xticks([])  # Remove x-axis tick marks
        ax.set_xticklabels([])  # Remove x-axis labels
        
        # Plot the CPU usage history
        ax.plot(history, color='#ff9999')
        ax.set_title("CPU Usage", color='white')
        ax.set_ylabel("CPU Usage (%)", color='white')
        ax.set_ylim(0, 100)  # Limit Y axis to 0-100%

        ax.text(0.05, 0.95, f"Current CPU Usage: {cpu_usage:.2f}%", 
            transform=ax.transAxes,  # Relative to the plot
            fontsize=12, 
            verticalalignment='top', 
            color='white')

        # Save the plot to a BytesIO object
        buffer = BytesIO()
        fig.savefig(buffer, format='png')
        buffer.seek(0)

        # Convert the PNG to a QPixmap to display in PyQt
        pixmap = QPixmap()
        pixmap.loadFromData(buffer.read())
        return pixmap
    

def main():
    app = QApplication(sys.argv)

    backend = Backend()
    window = MainWindow(backend)
    window.show()

    sys.exit(app.exec())


if __name__ == '__main__':
    main()
