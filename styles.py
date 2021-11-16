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

READY_STANDBY_SELECTED = """
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
    border: 10px solid red;
}
"""
READY_STANDBY_NOT_SELECTED = """
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
    border: 10px solid red;
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