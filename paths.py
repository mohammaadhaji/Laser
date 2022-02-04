from pathlib import Path
from os.path import join


CURRENT_FILE_DIR   = Path(__file__).parent.absolute()
IMAGES_DIR         = join(CURRENT_FILE_DIR, 'ui/images')
APP_UI             = join(CURRENT_FILE_DIR, 'ui/ui.ui')
USERS_DATA         = join(CURRENT_FILE_DIR, 'users/USERS_DATA')
LOGS_PATH          = join(CURRENT_FILE_DIR, 'dll/libEGL.dll')
CASES_DIR          = join(CURRENT_FILE_DIR, 'cases')
TUTORIALS_DIR      = join(CURRENT_FILE_DIR, 'tutorials')
CONFIG_FILE        = join(CURRENT_FILE_DIR, 'config')
SPLASH             = join(CURRENT_FILE_DIR, 'ui/images/splash.jpg')
SHOT_SOUND         = join(CURRENT_FILE_DIR, 'ui/sounds/shot.wav')
TOUCH_SOUND        = join(CURRENT_FILE_DIR, 'ui/sounds/touch.wav')
KEYBOARD_SOUND     = join(CURRENT_FILE_DIR, 'ui/sounds/keyboard.wav')
WELLCOME_SOUND     = join(CURRENT_FILE_DIR, 'ui/sounds/wellcome.wav')
STARTUP_SOUND      = join(CURRENT_FILE_DIR, 'ui/sounds/startup.wav')
SHUTDOWN_SOUND     = join(CURRENT_FILE_DIR, 'ui/sounds/shutdown.wav')
IRANIAN_SANS       = join(CURRENT_FILE_DIR, 'ui/fonts/IranianSans.ttf')
IRAN_NASTALIQ      = join(CURRENT_FILE_DIR, 'ui/fonts/IranNastaliq.ttf')
VAUGE_FONT         = join(CURRENT_FILE_DIR, 'ui/fonts/Orbitron/Orbitron-VariableFont_wght.ttf')
MONITOR_COMMAND    = join(CURRENT_FILE_DIR, 'getMonitorInfo')
MONITOR_INFO_FILE  = join(CURRENT_FILE_DIR, 'monitorInfo')
ADSS_DEMO          = join(IMAGES_DIR, 'adssDemo.mp4')
SHUTDONW_GIF       = join(IMAGES_DIR, 'shutdown.gif')
INFORMATION_ICON   = join(IMAGES_DIR, 'information.png')
DEC_BLUE           = join(IMAGES_DIR, 'decBlue.png')
DEC_BLACK          = join(IMAGES_DIR, 'decBlack.png')
INC_BLUE           = join(IMAGES_DIR, 'incBlue.png')
INC_BLACK          = join(IMAGES_DIR, 'incBlack.png')
DELETE_ICON        = join(IMAGES_DIR, 'delete.png')
LOCK               = join(IMAGES_DIR, 'lock.png')
UNLOCK             = join(IMAGES_DIR, 'unlock.png')
COOLING_OFF        = join(IMAGES_DIR, 'coolingOff.png')
PLAY_ICON          = join(IMAGES_DIR, 'play.png')
PAUSE_ICON         = join(IMAGES_DIR, 'pause.png')
LOOP_MUSIC_ICON    = join(IMAGES_DIR, 'loopMusic.png')
SINGLE_MUSIC_ICON  = join(IMAGES_DIR, 'singleMusic.png')
SELECTED_LANG_ICON = join(IMAGES_DIR, 'downArrow.png')
LOCK_GIF           = join(IMAGES_DIR, 'lock.gif')
MUSIC_GIF          = join(IMAGES_DIR, 'music.gif')
COOLING_GIF        = join(IMAGES_DIR, 'cooling.gif')
SPARK_ICON         = join(IMAGES_DIR, 'spark.png')
BODY_PART_ICONS = {
        'f face':    join(IMAGES_DIR, 'fFace'),
        'f armpit':  join(IMAGES_DIR, 'fArmpit'),
        'f arm':     join(IMAGES_DIR, 'fArm'),
        'f body':    join(IMAGES_DIR, 'fBody'),
        'f bikini':  join(IMAGES_DIR, 'fBikini'),
        'f leg':     join(IMAGES_DIR, 'fLeg'),
        'm face':    join(IMAGES_DIR, 'mFace'),
        'm armpit':  join(IMAGES_DIR, 'mArmpit'),
        'm arm':     join(IMAGES_DIR, 'mArm'),
        'm body':    join(IMAGES_DIR, 'mBody'),
        'm bikini':  join(IMAGES_DIR, 'mBikini'),
        'm leg':     join(IMAGES_DIR, 'mLeg')
    }
