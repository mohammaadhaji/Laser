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

APP_LOCK_BG = """
background-color: rgb(77, 74, 78);
color: white;
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

SLIDER = """
QSlider::groove:horizontal {
    border-radius: 1px;
    height: 3px;
    margin: 0px;
    background-color: rgb(52, 59, 72);
}
QSlider::groove:horizontal:hover {
    background-color: rgb(55, 62, 76);
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

SLIDER_SAVED = """
QSlider::groove:horizontal {
    border-radius: 1px;
    height: 3px;
    margin: 0px;
    background-color: rgb(52, 59, 72);
}
QSlider::groove:horizontal:hover {
    background-color: rgb(55, 62, 76);
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

SLIDER_DISABLED = """
QSlider::groove:horizontal {
    border-radius: 1px;
    height: 3px;
    margin: 0px;
    background-color: rgb(52, 59, 72);
}
QSlider::groove:horizontal:hover {
    background-color: rgb(55, 62, 76);
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

OWNER_INFO_STYLE = '''
QLabel {
    qproperty-alignment: AlignCenter;
	border: 1px solid #FF17365D;
	border-top-right-radius: 15px;
	background-color: #FF17365D;
	padding: 50px 50px;
	color: rgb(255, 255, 255);
	max-height: 100px;	
}
'''
