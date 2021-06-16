import sys
from interface import design
from PyQt5 import QtWidgets
from PyQt5.QtGui import QPixmap


from interface.handlers import settings_handlers
from pos_detector import make_shot
from action import calibrating_mode, calibrating_mode_simple, scaling_mode, write_in_json, calculate_mean_coeffs, calibration_points
from calculation import get_alpha, get_beta, get_gamma


class SCApp(QtWidgets.QMainWindow, design.Ui_MainWindow):
    def __init__(self):
        # Инициализация файла и получение доступа к шаблону
        super().__init__()
        self.setupUi(self)
        startup_pixmap = QPixmap('interface/bmstu.png') # Подставляем картинку
        self.img_label.setPixmap(startup_pixmap)

        # Кнопка выхода
        self.exitButton.clicked.connect(self.close)

        # Определение выпадающего меню в settings
        self.drive_letter_box.addItems(settings_handlers.get_driveLabels())
        self.scaling_file_input.addItems(settings_handlers.get_presetFiles())

        # Работа с калибровкой
        self.calibrate_button.clicked.connect(self.choose_calibrating_mode)

        # Работа со взвешиванием
        self.scale_button.clicked.connect(self.run_scaling_mode)

        # Реакция при выборе картинки в выпадающем меню
        self.image_list.currentTextChanged.connect(self.load_image)

        # Сделать пристрелочный снимок
        self.show_camera.clicked.connect(self.show_images)

    # Прогрузка нужного изображения в окно
    def load_image(self):
        image = self.image_list.currentText()
        pixmap = QPixmap(image) # Подставляем картинку
        self.img_label.setPixmap(pixmap)

    def show_images(self):
        image_pack = settings_handlers.image_shower(
            self.drive_letter_box.currentText())
        self.image_list.clear()
        self.image_list.addItems(image_pack)

    def choose_calibrating_mode(self):
        if self.simple_mode.isChecked():
            self.run_calibrating_mode_simple()
        else:
            self.run_calibrating_mode()


    def run_calibrating_mode(self):
        if self.global_prefs_check() and self.calibrating_prefs_check():
            settings_handlers.image_remover(self.drive_letter_box.currentText())
            n_steps = len(calibration_points)
            self.cal_progress.setMaximum(n_steps)
            self.messageBox("Уведомление",
                            "Для корректной калибровки убедитесь что плафторма достаточно\nосвещена, все точки попадают в кадр и грузик установлен в центре",
                            QtWidgets.QMessageBox.Information)
            global_json = {}
            alpha = 0
            for step in range(n_steps):
                step_json = calibrating_mode(self.logging_calibrating,
                                 self.shots_input.value(), step, n_steps,
                                 self.cal_weight_input.value())
                coeffs = [0, 0, 0]
                if step == 0:
                    coeffs[0] = get_alpha(step_json['scaled_value'],
                                          step_json['weight'])
                    alpha = coeffs[0]
                if step == 1 or step == 3:
                    coeffs[1] = get_beta(
                        step_json['scaled_value'], step_json['weight'],
                        step_json['relative_rect_pos_mean'][0], alpha)
                if step == 2 or step == 4:
                    coeffs[2] = get_gamma(
                        step_json['scaled_value'], step_json['weight'],
                        step_json['relative_rect_pos_mean'][1], alpha)
                step_json['coeffs'] = coeffs
                global_json[f'Stage {step}'] = step_json
                self.cal_progress.setValue(step + 1)
                image_pack = settings_handlers.image_shower(self.drive_letter_box.currentText())
                self.image_list.clear()
                self.image_list.addItems(image_pack)
                if step != (n_steps-1):
                    self.messageBox("Уведомление",
                                    f"Установите грузик в позицию {step+1}",
                                    QtWidgets.QMessageBox.Information)
                else:
                    self.messageBox("Уведомление",
                                    "Процесс калибровки завершен, данные сохранены в файл",
                                    QtWidgets.QMessageBox.Information)
            global_json['Result'] = calculate_mean_coeffs(global_json)
            write_in_json(self.sensor_name_input.text(), global_json)


    def run_calibrating_mode_simple(self):
        if self.global_prefs_check() and self.calibrating_prefs_check():
            settings_handlers.image_remover(
                self.drive_letter_box.currentText())
            n_steps = len(calibration_points)
            self.cal_progress.setMaximum(n_steps)
            self.messageBox(
                "Уведомление",
                "Для корректной калибровки убедитесь что плафторма достаточно\nосвещена, все точки попадают в кадр и грузик установлен в центре",
                QtWidgets.QMessageBox.Information)
            global_json = {}
            for step in range(n_steps):
                step_json = calibrating_mode_simple(self.logging_calibrating,
                                             self.shots_input.value(), step,
                                             n_steps,
                                             self.cal_weight_input.value())
                coeffs = [0, 0, 0]
                coeffs[0] = get_alpha(step_json['scaled_value'],
                                        step_json['weight'])
                step_json['coeffs'] = coeffs
                global_json[f'Stage {step}'] = step_json
                self.cal_progress.setValue(step + 1)
                image_pack = settings_handlers.image_shower(
                    self.drive_letter_box.currentText())
                self.image_list.clear()
                self.image_list.addItems(image_pack)
                if step != (n_steps - 1):
                    self.messageBox("Уведомление",
                                    f"Установите грузик в позицию {step+1}",
                                    QtWidgets.QMessageBox.Information)
                else:
                    self.messageBox(
                        "Уведомление",
                        "Процесс калибровки завершен, данные сохранены в файл",
                        QtWidgets.QMessageBox.Information)
            global_json['Result'] = calculate_mean_coeffs(global_json)
            JSON_name = self.sensor_name_input.text()
            write_in_json(JSON_name + '_simple', global_json)


    def run_scaling_mode(self):
        if self.global_prefs_check() and self.scaling_prefs_check():
            scaling_mode(self.logging_scaling,
                         self.shots_input.value(),
                         self.scaling_file_input.currentText())


    def single_shot(self):
        make_shot()
        image_pack = settings_handlers.image_shower(self.drive_letter_box.currentText())
        self.image_list.addItems(image_pack)


    def global_prefs_check(self):
        if isinstance(self.shots_input.value(), int) and (self.shots_input.value()>1):
            return True
        elif isinstance(self.shots_input.value(), int) and (self.shots_input.value()==1):
            if self.messageBox("Уведомление",
                               "Не рекомендуется ставить один снимок",
                               QtWidgets.QMessageBox.Information):
                return True
        else:
            self.messageBox("Предупреждение",
                            "Настройки приложения не корректны!",
                            QtWidgets.QMessageBox.Critical)
            return False


    def calibrating_prefs_check(self):
        if isinstance(self.cal_weight_input.value(), int) and (self.cal_weight_input.value()>0) and self.sensor_name_input.text():
            self.logging_calibrating.appendPlainText(
                f"Sensor type: {self.sensor_name_input.text()}")
            return True
        else:
            self.messageBox("Предупреждение",
                            "Настройки приложения не корректны!",
                            QtWidgets.QMessageBox.Critical)
            return False


    def scaling_prefs_check(self):
        if self.scaling_file_input.maxCount()>1:
            return True
        else:
            return False


    def messageBox(self, title, body, icontype=QtWidgets.QMessageBox.Information):
        msgBox = QtWidgets.QMessageBox()
        msgBox.setIcon(icontype)
        msgBox.setText(body)
        msgBox.setWindowTitle(title)
        msgBox.setStandardButtons(QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Cancel)
        returnValue = msgBox.exec()
        if returnValue == QtWidgets.QMessageBox.Ok:
            return True
        elif returnValue == QtWidgets.QMessageBox.Cancel:
            return False


def main():
    app = QtWidgets.QApplication(sys.argv)  # Новый экземпляр QApplication
    window = SCApp()  # Создаём объект класса SCApp
    window.show()  # Показываем окно
    app.exec_()  # и запускаем приложение


if __name__ == '__main__':  # Если мы запускаем файл напрямую, а не импортируем
    main()  # то запускаем функцию main()
