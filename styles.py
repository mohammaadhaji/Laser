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

SELECTED_BODYPART = """
QPushButton {
    background-color: rgb(213, 213, 213);
    color: rgb(0, 0, 0);
    min-width: 140px;
    min-height: 140px;
    max-width: 150px;
    max-height: 150px;
    border-radius: 15px;
    border: 10px solid red;
    outline:0;
}
QPushButton:hover:!pressed{
    background-color: rgb(255, 255, 255);
    border: 10px solid  red;
}
"""

NOT_SELECTED_BODYPART = """
QPushButton {
    background-color: rgb(213, 213, 213);
    color: rgb(0, 0, 0);
    min-width: 140px;
    min-height: 140px;
    max-width: 150px;
    max-height: 150px;
    border-radius: 15px;
    border: 10px solid rgb(213, 213, 213);
    outline:0;
}
QPushButton:hover:!pressed{
    background-color: rgb(255, 255, 255);
    border: 10px solid  rgb(255, 255, 255);
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
QPushButton {
    background-color: rgb(213, 213, 213);
    color: rgb(0, 0, 0);
    max-width: 80px;
    max-height: 80px;
    border-radius: 15px;
    border: 8px solid red;
    outline:0;
}
QPushButton:hover:!pressed{
    background-color: rgb(255, 255, 255);
    border: 10px solid red;
}
"""

EPF_NOT_SELECTED = """
QPushButton {
    background-color: rgb(213, 213, 213);
    color: rgb(0, 0, 0);
    max-width: 80px;
    max-height: 80px;
    border-radius: 15px;
    border: 8px solid rgb(213, 213, 213);
    outline:0;
}
QPushButton:hover:!pressed{
    background-color: rgb(255, 255, 255);
    border: 10px solid rgb(255, 255, 255);
}
"""