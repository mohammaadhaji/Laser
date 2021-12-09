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

EPF_SELECTED = """
QPushButton{
    outline : 0;
    background-color: rgb(213, 213, 213);
    border-radius: 15px;
    border: 10px solid red;
}

QPushButton:pressed{
    border: 10px solid red;
}
"""

# EPF: Energy, Pulse Width, Frequency
EPF_NOT_SELECTED = """ 
QPushButton{
    outline : 0;
    background-color: rgb(213, 213, 213);
    border-radius: 15px;
    border: 10px solid rgb(213, 213, 213);
}
QPushButton:pressed{
    border: 10px solid red;
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
"""

APP_BG = """
background-color: rgb(32, 74, 135);
color: rgb(255, 255, 255);
"""