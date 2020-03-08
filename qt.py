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
		self.mim_file_name = ""
		self.save_location = ""
		self.result_list = []
		self.e = eg.Engine()
		self.title = "/중복불허"
		self.current_info  = "진행 상태: 대기 중 입니다."


	def setupUI(self):

		self.setGeometry(1200, 600, 400, 400)
		self.setWindowTitle("알류미늄 폭조합")

		self.orderButton = QPushButton("Order File Open")
		self.orderButton.clicked.connect(self.pushOrderButtonClicked)

		self.materialButton = QPushButton("material File Open")
		self.materialButton.clicked.connect(self.pushmaterialButtonClicked)

		self.mimButton = QPushButton("mim File Open")
		self.mimButton.clicked.connect(self.pushmimButtonClicked)

		self.save_location_Button = QPushButton("Result File location Folder")
		self.save_location_Button.clicked.connect(self.save_location_ButtonClicked)

		self.alloy_list=[]
		alloy = ["A1050","A1235","A1100","A8079","A3003","A8021","F308","F309","BRW04"]

		#file location
		self.order_file_location_label = QLabel(self)
		self.material_file_location_label= QLabel(self)
		self.mim_file_location_label= QLabel(self)
		self.save_location_label= QLabel(self)

		self.current_info_label= QLabel(self)
		self.current_info_label.setText("진행 상태: 대기 중 입니다.")
		#self.current_info  = "진행 상태: 대기 중 입니다."
		# Create textbox
		self.textbox1 = QLineEdit("1",self)
		#self.textbox2 = QLineEdit("0.3",self)
		added_location = 30

		#MG_weight box
		self.w_MG_label = QLabel(self)
		self.w_MG_label.setText("MG 평가함수")
		self.w_MG_label.move(15,175+added_location)
		self.w_MG_label_ = QLabel(self)
		self.w_MG_label_.setText("ex) 0.3")
		self.w_MG_label_.move(100,175+added_location)

		self.w_MG_label1 = QLabel(self)
		self.w_MG_label1.setText("낭비폭 비중")
		self.w_MG_label1.move(5,200+added_location)
		self.w_MG_textbox1 = QLineEdit(self)
		self.w_MG_textbox1.move(95,205+added_location)
		self.w_MG_textbox1.resize(30,20)

		self.w_MG_label2 = QLabel(self)
		self.w_MG_label2.setText("분리항 비중")
		self.w_MG_label2.move(150,200+added_location)
		self.w_MG_textbox2 = QLineEdit(self)
		self.w_MG_textbox2.move(225,205+added_location)
		self.w_MG_textbox2.resize(30,20)

		self.w_MG_label3 = QLabel(self)
		self.w_MG_label3.setText("초과생산량 비중")
		self.w_MG_label3.move(5,220+added_location)
		self.w_MG_textbox3 = QLineEdit(self)
		self.w_MG_textbox3.move(95,225+added_location)
		self.w_MG_textbox3.resize(30,20)

		self.w_MG_label4 = QLabel(self)
		self.w_MG_label4.setText("낭비량 비중")
		self.w_MG_label4.move(150,220+added_location)
		self.w_MG_textbox4 = QLineEdit(self)
		self.w_MG_textbox4.move(225,225+added_location)
		self.w_MG_textbox4.resize(30,20)

		#BG_weight box
		self.w_BG_label = QLabel(self)
		self.w_BG_label.setText("BG 평가함수")
		self.w_BG_label.move(15,250+added_location)
		self.w_BG_label_ = QLabel(self)
		self.w_BG_label_.setText("ex) 0.3")
		self.w_BG_label_.move(100,250+added_location)

		self.w_BG_label1 = QLabel(self)
		self.w_BG_label1.setText("총 부족생산량 비중")
		self.w_BG_label1.move(5,275+added_location)
		self.w_BG_textbox1 = QLineEdit(self)
		self.w_BG_textbox1.move(115,280+added_location)
		self.w_BG_textbox1.resize(30,20)

		self.w_BG_label2 = QLabel(self)
		self.w_BG_label2.setText("총 초과생산량 비중")
		self.w_BG_label2.move(150,275+added_location)
		self.w_BG_textbox2 = QLineEdit(self)
		self.w_BG_textbox2.move(265,280+added_location)
		self.w_BG_textbox2.resize(30,20)

		self.w_BG_label3 = QLabel(self)
		self.w_BG_label3.setText("총 낭비량 비중")
		self.w_BG_label3.move(5,295+added_location)
		self.w_BG_textbox3 = QLineEdit(self)
		self.w_BG_textbox3.move(115,300+added_location)
		self.w_BG_textbox3.resize(30,20)

		for i in alloy:
			self.alloy_list.append(QCheckBox(i, self))

		self.check_overlap = QCheckBox("중복 허용", self)
		self.btn1 = QPushButton('Start combination', self)
		self.btn1.setCheckable(True)
		self.btn1.clicked.connect(self.grouping)

		self.btn2 = QPushButton('Save result excel', self)
		self.btn2.setCheckable(True)
		self.btn2.clicked.connect(self.toXLS)

		self.label1 = QLabel(self)
		self.label1.setText("시뮬레이션 횟수 ex) 1")
		#self.label2 = QLabel(self)
		#self.label2.setText("추가 생산량 비율(소수점 단위로 입력 ex)0.3 )")
		self.label3 = QLabel(self)
		self.label3.setText("조합할 ALLOY 종류를 선택하세요.")
		self.empty = QLabel(self)

		layout = QVBoxLayout()
		layout.addWidget(self.orderButton)
		layout.addWidget(self.order_file_location_label)
		layout.addWidget(self.materialButton)
		layout.addWidget(self.material_file_location_label)
		layout.addWidget(self.mimButton)
		layout.addWidget(self.mim_file_location_label)
		layout.addWidget(self.save_location_Button)
		layout.addWidget(self.save_location_label)
		layout.addWidget(self.empty)


		for i in range(8):
			layout.addWidget(self.empty)
		layout.addWidget(self.label1)
		layout.addWidget(self.textbox1)
		layout.addWidget(self.check_overlap)

		layout.addWidget(self.label3)
		for i in range(len(alloy)):
			layout.addWidget(self.alloy_list[i])
		layout.addWidget(self.empty)
		layout.addWidget(self.btn1)
		layout.addWidget(self.current_info_label)

		layout.addWidget(self.btn2)
		self.setLayout(layout)

	def grouping(self):
		self.current_info = "진행 상태: 조합 중 입니다."
		self.current_info_label.setText(self.current_info)
		QMessageBox.about(self, "알림창", "조합을 시작하였습니다.")

		select_alloy_list = []
		for i in range(len(self.alloy_list)):
         		#alloy 선택
			if self.alloy_list[i].isChecked() == True:
				print(str(self.alloy_list[i].text()))
				select_alloy_list.append(str(self.alloy_list[i].text()))

		##조합 group 계산
		if(self.order_file_name!='' and self.material_file_name!='' and self.mim_file_name!=''):
			overlap=False
			if self.check_overlap.isChecked() == True:
				overlap = True
				self.title = "/중복허용"

			self.e = eg.Engine(self.order_file_name[0],self.material_file_name[0],self.mim_file_name[0],overlap)
			if self.w_MG_textbox1.text()!="":
				self.e.weight_extra_width = float(self.w_MG_textbox1.text())
			if self.w_MG_textbox2.text()!="":
				self.e.weight_combi_count = float(self.w_MG_textbox2.text())
			if self.w_MG_textbox3.text()!="":
				self.e.weight_over_production = float(self.w_MG_textbox3.text())
			if self.w_MG_textbox4.text()!="":
				self.e.weight_residual_material = float(self.w_MG_textbox4.text())

			if self.w_BG_textbox1.text()!="":
				self.e.weight_need_combi = float(self.w_BG_textbox1.text())
			if self.w_BG_textbox2.text()!="":
				self.e.weight_over_production_ratio = float(self.w_BG_textbox2.text())
			if self.w_BG_textbox3.text()!="":
				self.e.weight_wasted_materail = float(self.w_BG_textbox3.text())

			self.e.read_file()


			for i in range(len(select_alloy_list)):
				temp_e = deepcopy(self.e)
				num_of_thread = int(self.textbox1.text())
				#residual_rate = float(self.textbox2.text())

				if num_of_thread>10:
					num_of_loop = int(num_of_thread/10)
					remainder = num_of_thread%10
					for j in range(num_of_loop-1):
						temp_e.run_thread(select_alloy_list[i],10)

					temp_e.run_thread(select_alloy_list[i],remainder)
				else:
					temp_e.run_thread(select_alloy_list[i],num_of_thread)

				self.result_list.append([select_alloy_list[i],temp_e.select_best_result()])
				del temp_e

			QMessageBox.about(self, "알림창", "성공적으로 조합하였습니다.")
			self.current_info = "진행 상태: 성공적으로 조합하였습니다."
			self.current_info_label.setText(self.current_info)

		else:
			QMessageBox.about(self, "알림창", "File을 설정하지 않으셨습니다.")
			self.current_info = "진행 상태: 대기 중 입니다."
			self.current_info_label.setText(self.current_info)

	def toXLS(self):
		if(self.result_list != []):
			for i in range(len(self.result_list)):

				self.e.save_excel(self.result_list[i][0],self.result_list[i][1],self.save_location+self.title)

			QMessageBox.about(self, "알림창", "성공적으로 저장하셨습니다.")
		else:
			QMessageBox.about(self, "알림창", "조합하지 않으셨습니다.")

	def pushOrderButtonClicked(self):
		self.order_file_name = QFileDialog.getOpenFileName(self)
		self.order_file_location_label.setText(self.order_file_name[0])
		for i in range(len(self.order_file_name[0])):
			if self.order_file_name[0][len(self.material_file_name)-i-1] == "/":
				self.save_location = self.order_file_name[0][0:(len(self.material_file_name)-i)]
				break


	def pushmaterialButtonClicked(self):
		self.material_file_name = QFileDialog.getOpenFileName(self)
		self.material_file_location_label.setText(self.material_file_name[0])

	def pushmimButtonClicked(self):
		self.mim_file_name = QFileDialog.getOpenFileName(self)
		self.mim_file_location_label.setText(self.mim_file_name[0])

	def save_location_ButtonClicked(self):
		self.save_location = QFileDialog.getExistingDirectory(self)
		self.save_location_label.setText(self.save_location)

if __name__ == "__main__":
	app = QApplication(sys.argv)
	window = MyWindow()
	window.show()
	app.exec_()
