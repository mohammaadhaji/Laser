SELECTED_SEX = """
QPushButton {
    background-color: rgb(213, 213, 213);
    color: rgb(0, 0, 0);
    min-width: 170px;
    min-height: 80px;
    border-radius: 15px;
    border: 10px solid red;
    outline:0;
}
QPushButton:hover:!pressed{
    background-color: rgb(255, 255, 255);
}
"""

NOT_SELECTED_SEX = """
QPushButton {
    background-color: rgb(213, 213, 213);
    color: rgb(0, 0, 0);
    min-width: 170px;
    min-height: 80px;
    border-radius: 15px;
    border: 10px solid rgb(213, 213, 213);
    outline:0;
}
QPushButton:hover:!pressed{
    background-color: rgb(255, 255, 255);
    border: 10px solid rgb(255, 255, 255);
}
"""


SHIFT_PRESSED = """
QPushButton{
    min-width:120px;
    background-color: rgb(0, 170, 255);
    color:balck;
}
"""

SHIFT = """
QPushButton{
    min-width:120px;
}
"""

FARSI_PRESSED = """
QPushButton{
    background-color: rgb(0, 170, 255);
    color:balck;
}
"""

SELECTED_CASE = """
QPushButton {
    outline:0;
    border-radius:45px;
    background-color: rgb(255, 0, 0);
}
QPushButton:pressed{
    background-color: rgb(255, 0, 0);
}
"""

NOT_SELECTED_CASE = """
QPushButton {
    outline:0;
    border-radius:45px;
    background-color: rgb(213, 213, 213);

}
QPushButton:pressed{
    background-color: rgb(255, 0, 0);
}
"""

TXT_HW_PASS = """
QLineEdit{
    border-radius:10px;
    border:2px solid gray;
    padding:10px 10px 10px 10px;
}
QLineEdit:focus{
    border:2px solid white;
}
"""
TXT_HW_WRONG_PASS = """
QLineEdit{
    border-radius:10px;
    border:3px solid red;
    padding:10px 10px 10px 10px;
}
QLineEdit:focus{
    border:2px solid white;
}
"""

APP_BG = """
background-color: rgb(32, 74, 135);
color: rgb(255, 255, 255);
"""

READY_SELECTED = """
QPushButton {
    background-color: rgb(213, 213, 213);
    color: rgb(0, 0, 0);
    min-width: 170px;
    min-height: 80px;
    border-radius: 15px;
    border: 10px solid red;
    outline:0;
}
QPushButton:pressed{
    background-color: rgb(0, 170, 255);
    border: 10px solid red;
}
"""

READY_NOT_SELECTED = """
QPushButton {
    background-color: rgb(213, 213, 213);
    color: rgb(0, 0, 0);
    min-width: 170px;
    min-height: 80px;
    border-radius: 15px;
    border: 10px solid rgb(213, 213, 213);
    outline:0;
}
QPushButton:pressed{
    background-color: rgb(0, 170, 255);
    border: 10px solid rgb(0, 170, 255);
}
"""

ACTION_BTN = """
QPushButton {
    border-radius:10px;
    outline:0;
}
QPushButton:pressed{
    margin: 10px 0 0 0;
}
"""

SLIDER_GW = """
QSlider::groove:horizontal {
    border-radius: 1px;
    height: 3px;
    margin: 0px;
    background-color: white;
}

QSlider::handle:horizontal {
    background-color: rgb(85, 170, 255);
    border: none;
    height: 80px;
    width: 80px;
    border-radius: 40px;
    margin: -40px 0;
    padding: -40px 0px;
}
QSlider::handle:horizontal:pressed {
    background-color: rgb(65, 255, 195);
}
"""

SLIDER_DISABLED_GW = """
QSlider::groove:horizontal {
    border-radius: 1px;
    height: 3px;
    margin: 0px;
    background-color: white;
}

QSlider::handle:horizontal {
    background-color: rgb(157, 157, 157);
    border: none;
    height: 80px;
    width: 80px;
    border-radius: 40px;
    margin: -40px 0;
    padding: -40px 0px;
}
QSlider::handle:horizontal:pressed {
    background-color: rgb(65, 255, 195);
}
"""

SLIDER_GB = """
QSlider::groove:horizontal {
    border-radius: 1px;
    height: 3px;
    margin: 0px;
    background-color: black;
}

QSlider::handle:horizontal {
    background-color: rgb(85, 170, 255);
    border: none;
    height: 80px;
    width: 80px;
    border-radius: 40px;
    margin: -40px 0;
    padding: -40px 0px;
}
QSlider::handle:horizontal:pressed {
    background-color: rgb(65, 255, 195);
}
"""

SLIDER_DISABLED_GB = """
QSlider::groove:horizontal {
    border-radius: 1px;
    height: 3px;
    margin: 0px;
    background-color: black;
}

QSlider::handle:horizontal {
    background-color: rgb(157, 157, 157);
    border: none;
    height: 80px;
    width: 80px;
    border-radius: 40px;
    margin: -40px 0;
    padding: -40px 0px;
}
QSlider::handle:horizontal:pressed {
    background-color: rgb(65, 255, 195);
}
"""

SLIDER_SAVED_GB = """
QSlider::groove:horizontal {
    border-radius: 1px;
    height: 3px;
    margin: 0px;
    background-color: black;
}

QSlider::handle:horizontal {
    background-color: white;
    border: none;
    height: 80px;
    width: 80px;
    border-radius: 40px;
    margin: -40px 0;
    padding: -40px 0px;
}
QSlider::handle:horizontal:pressed {
    background-color: rgb(65, 255, 195);
}
"""

SLIDER_SAVED_GW = """
QSlider::groove:horizontal {
    border-radius: 1px;
    height: 3px;
    margin: 0px;
    background-color: white;
}

QSlider::handle:horizontal {
    background-color: white;
    border: none;
    height: 80px;
    width: 80px;
    border-radius: 40px;
    margin: -40px 0;
    padding: -40px 0px;
}
QSlider::handle:horizontal:pressed {
    background-color: rgb(65, 255, 195);
}
"""

OWNER_INFO_STYLE_FA = '''
QLabel {
    font: 40pt "IranNastaliq";
	border: 5px solid #FF17365D;
	border-top-right-radius: 15px;
	background-color: #FF17365D;
    padding: 30px 50px 50px 50px;
	color: rgb(255, 255, 255);
}
'''

OWNER_INFO_STYLE_EN = '''
QLabel {
    font: 40pt "Aril";
	border: 5px solid #FF17365D;
	border-top-right-radius: 15px;
	background-color: #FF17365D;
	padding: 50px 50px;
	color: rgb(255, 255, 255);
}
'''

BTN_COLOR1 = """
QPushButton{
    background-color: rgb(32, 74, 135);
    min-width: 150px;
    min-height: 100px;
    max-width: 150px;
    max-height: 100px;
    border:5px solid white;
    border-radius:10px;
}
QPushButton:pressed{
    border:5px solid red;
}
"""

BTN_COLOR2 = """
QPushButton{
    background-color: rgb(173, 3, 252);
    min-width: 150px;
    min-height: 100px;
    max-width: 150px;
    max-height: 100px;
    border:5px solid white;
    border-radius:10px;
}
QPushButton:pressed{
    border:5px solid red;
}
"""

BTN_COLOR3 = """
QPushButton{
    background-color: rgb(20, 20, 20);
    min-width: 150px;
    min-height: 100px;
    max-width: 150px;
    max-height: 100px;
    border:5px solid white;
    border-radius:10px;
}
QPushButton:pressed{
    border:5px solid red;
}
"""

BTN_COLOR4 = """
QPushButton{
    background-color: rgb(252, 3, 128);
    min-width: 150px;
    min-height: 100px;
    max-width: 150px;
    max-height: 100px;
    border:5px solid white;
    border-radius:10px;
}
QPushButton:pressed{
    border:5px solid red;
}
"""

BTN_THEME1 = """
QPushButton{
    background-color:black;
    background-image: url(ui/images/theme1.jpg);
    background-position: center;
    background-repeat: no-repeat;
    min-width: 150px;
    min-height: 100px;
    max-width: 150px;
    max-height: 100px;
    border:5px solid white;
    border-radius:10px;
}
QPushButton:pressed{
    border:5px solid red;
}
"""

BTN_THEME2 = """
QPushButton{
    background-color:black;
    background-image: url(ui/images/theme2.jpg);
    background-position: center;
    background-repeat: no-repeat;
    min-width: 150px;
    min-height: 100px;
    max-width: 150px;
    max-height: 100px;
    border:5px solid white;
    border-radius:10px;
}
QPushButton:pressed{
    border:5px solid red;
}
"""

BTN_THEME3 = """
QPushButton{
    background-color:black;
    background-image: url(ui/images/theme3.jpg);
    background-position: center;
    background-repeat: no-repeat;
    min-width: 150px;
    min-height: 100px;
    max-width: 150px;
    max-height: 100px;
    border:5px solid white;
    border-radius:10px;
}
QPushButton:pressed{
    border:5px solid red;
}
"""

BTN_THEME4 = """
QPushButton{
    background-color:black;
    background-image: url(ui/images/theme4.jpg);
    background-position: center;
    background-repeat: no-repeat;
    min-width: 150px;
    min-height: 100px;
    max-width: 150px;
    max-height: 100px;
    border:5px solid white;
    border-radius:10px;
}
QPushButton:pressed{
    border:5px solid red;
}
"""

APP_LOCK_BG = """
    background-color: rgb(77, 74, 78);
"""

COLOR1 = """
    background-color: rgb(32, 74, 135); 
"""

COLOR2 = """
    background-color: rgb(173, 3, 252);
"""

COLOR3 = """
    background-color: rgb(20, 20, 20);
"""

COLOR4 = """
    background-color: rgb(252, 3, 128);
"""

THEME1 = """
QWidget#centralwidget {
    background-color: rgb(32, 74, 135);
    background-image: url(ui/images/wallpaper1.jpg); 
}
"""

THEME2 = """
QWidget#centralwidget {
    background-color: rgb(32, 74, 135);
    background-image: url(ui/images/wallpaper2.jpg); 
}
"""

THEME3 = """
QWidget#centralwidget {
    background-color: rgb(32, 74, 135);
    background-image: url(ui/images/wallpaper3.jpg); 
}
"""

THEME4 = """
QWidget#centralwidget {
    background-color: rgb(32, 74, 135);
    background-image: url(ui/images/wallpaper4.jpg); 
}
"""

CHECKBOX_DEL = """
QCheckBox { margin-bottom: 5px; outline:0}
QCheckBox::indicator { width : 50; height : 50; }
QCheckBox::indicator::unchecked { image : url(ui/images/unchecked.png); }
QCheckBox::indicator::checked { image : url(ui/images/checked.png); }
"""