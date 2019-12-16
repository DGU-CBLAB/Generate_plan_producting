import engine as eg
import sys
import pandas as pd
from PyQt5.QtWidgets import *
from datetime import datetime

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


		for i in alloy:
			self.alloy_list.append(QCheckBox(i, self))

		self.btn1 = QPushButton('Start combination', self)
		self.btn1.setCheckable(True)
		self.btn1.clicked.connect(self.grouping)

		self.btn2 = QPushButton('Save result excel', self)
		self.btn2.setCheckable(True)
		self.btn2.clicked.connect(self.toXLS)

		self.label = QLabel()

		layout = QVBoxLayout()
		layout.addWidget(self.orderButton)
		layout.addWidget(self.materialButton)
		for i in range(len(alloy)):
			layout.addWidget(self.alloy_list[i])

		layout.addWidget(self.label)
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
			for i in select_alloy_list:
				self.e.run_thread(i,20)
				self.result_list.append([i,self.e.select_best_result()])
				#selected_list, temp_order_group_data, temp_material_group_data = e.get_combination(i)
				#combi_df,result_df = e.get_result_data(selected_list, temp_order_group_data,temp_material_group_data)
				#self.result_list.append([i,combi_df,result_df])

			QMessageBox.about(self, "알림창", "성공적으로 조합하셨습니다.")
		else:
			QMessageBox.about(self, "알림창", "File을 설정하지 않으셨습니다.")

	def toXLS(self):
		if(self.result_list != []):
			for i in range(len(self.result_list)):
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
