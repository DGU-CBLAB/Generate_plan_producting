import engine as eg
import sys
import pandas as pd
from PyQt5.QtWidgets import *
from datetime import datetime
from copy import deepcopy

class MyWindow(QWidget):
	def __init__(self, option_num = 1):
		super().__init__()
		self.setupUI()
		self.order_file_name = ""
		self.material_file_name = ""
		self.result_list = []
		self.e = eg.Engine()

	def setupUI(self):

		self.setGeometry(1000, 500, 300, 300)
		self.setWindowTitle("알류미늄 폭조합")

		self.orderButton = QPushButton("Order File Open")
		self.orderButton.clicked.connect(self.pushOrderButtonClicked)

		self.materialButton = QPushButton("material File Open")
		self.materialButton.clicked.connect(self.pushmaterialButtonClicked)

		self.alloy_list=[]
		alloy = ["A1050","A1235","A1100","A8079","A3003","A8021","F308","F309","BRW04"]

		# Create textbox
		self.textbox1 = QLineEdit("시뮬레이션 횟수",self)
		self.textbox2 = QLineEdit("추가 생산량 비율",self)

		for i in alloy:
			self.alloy_list.append(QCheckBox(i, self))

		self.btn1 = QPushButton('Start combination', self)
		self.btn1.setCheckable(True)
		self.btn1.clicked.connect(self.grouping)

		self.btn2 = QPushButton('Save result excel', self)
		self.btn2.setCheckable(True)
		self.btn2.clicked.connect(self.toXLS)

		self.label1 = QLabel(self)
		self.label1.setText("시뮬레이션 횟수")
		self.label2 = QLabel(self)
		self.label2.setText("추가 생산량 비율(소수점 단위로 입력 ex)0.3 )")

		layout = QVBoxLayout()
		layout.addWidget(self.orderButton)
		layout.addWidget(self.materialButton)
		layout.addWidget(self.label1)
		layout.addWidget(self.textbox1)
		layout.addWidget(self.label2)
		layout.addWidget(self.textbox2)
		for i in range(len(alloy)):
			layout.addWidget(self.alloy_list[i])

		layout.addWidget(self.btn1)
		layout.addWidget(self.btn2)

		self.setLayout(layout)

	def grouping(self):

		select_alloy_list = []
		for i in range(len(self.alloy_list)):
         		#alloy 선택
			if self.alloy_list[i].isChecked() == True:
				print(str(self.alloy_list[i].text()))
				select_alloy_list.append(str(self.alloy_list[i].text()))

		##조합 group 계산
		if(self.order_file_name!='' and self.material_file_name!=''):
			self.e = eg.Engine(self.order_file_name[0],self.material_file_name[0])
			self.e.read_file()
			for i in range(len(select_alloy_list)):
				temp_e = deepcopy(self.e)
				num_of_thread = int(self.textbox1.text())
				residual_rate = float(self.textbox2.text())
				if num_of_thread>10:
					num_of_loop = int(nun_of_thread/10)
					remainder = nun_of_thread%10
					for j in range(num_of_loop-1):
						temp_e.run_thread(select_alloy_list[i],10,residual_rate)

					temp_e.run_thread(select_alloy_list[i],remainder,residual_rate)
				else:
					temp_e.run_thread(select_alloy_list[i],num_of_thread,residual_rate)

				self.result_list.append([select_alloy_list[i],temp_e.select_best_result()])
				del temp_e
				#self.e.save_excel(i,self.e.select_best_result())

			QMessageBox.about(self, "알림창", "성공적으로 조합하셨습니다.")
		else:
			QMessageBox.about(self, "알림창", "File을 설정하지 않으셨습니다.")

	def toXLS(self):
		if(self.result_list != []):
			for i in range(len(self.result_list)):
				#print(self.result_list[i][0],self.result_list[i][1])
				self.e.save_excel(self.result_list[i][0],self.result_list[i][1])

			QMessageBox.about(self, "알림창", "성공적으로 저장하셨습니다.")
		else:
			QMessageBox.about(self, "알림창", "조합하지 않으셨습니다.")

	def pushOrderButtonClicked(self):
		self.order_file_name = QFileDialog.getOpenFileName(self)


	def pushmaterialButtonClicked(self):
		self.material_file_name = QFileDialog.getOpenFileName(self)


if __name__ == "__main__":
	app = QApplication(sys.argv)
	window = MyWindow()
	window.show()
	app.exec_()
