from pathlib import Path
from os.path import join


CURRENT_FILE_DIR   = Path(__file__).parent.absolute()
IMAGES_DIR         = join(CURRENT_FILE_DIR, 'ui/images')
APP_UI             = join(CURRENT_FILE_DIR, 'ui/ui.ui')
USERS_DIR          = join(CURRENT_FILE_DIR, 'users')
CASES_DIR          = join(CURRENT_FILE_DIR, 'cases')
TUTORIALS_DIR      = join(CURRENT_FILE_DIR, 'tutorials')
CONFIG_FILE        = join(CURRENT_FILE_DIR, 'config')
SPLASH             = join(CURRENT_FILE_DIR, 'ui/images/splash.jpeg')
SHOT_SOUND         = join(CURRENT_FILE_DIR, 'ui/sounds/shot.wav')
TOUCH_SOUND        = join(CURRENT_FILE_DIR, 'ui/sounds/touch4.wav')
KEYBOARD_SOUND     = join(CURRENT_FILE_DIR, 'ui/sounds/touch3.wav')
WELLCOME_SOUND     = join(CURRENT_FILE_DIR, 'ui/sounds/wellcome.wav')
IRANIAN_SANS       = join(CURRENT_FILE_DIR, 'ui/fonts/IranianSans.ttf')
IRAN_NASTALIQ      = join(CURRENT_FILE_DIR, 'ui/fonts/IranNastaliq.ttf')
INFORMATION_ICON   = join(IMAGES_DIR, 'information.png')
DELETE_ICON        = join(IMAGES_DIR, 'delete.png')
WATERFLOW          = join(IMAGES_DIR, 'waterflow.png')
WATERFLOW_WARNING  = join(IMAGES_DIR, 'waterflowWarning.png')
TEMP               = join(IMAGES_DIR, 'temp.png')
TEMP_WARNING       = join(IMAGES_DIR, 'tempWarning.png')
WATERLEVEL         = join(IMAGES_DIR, 'waterLevel.png')
WATERLEVEL_WARNING = join(IMAGES_DIR, 'waterLevelWarning.png')
LOCK               = join(IMAGES_DIR, 'lock.png')
UNLOCK             = join(IMAGES_DIR, 'unlock.png')
LOCK_WARNING       = join(IMAGES_DIR, 'unlockWarning.png')
COOLING_OFF        = join(IMAGES_DIR, 'coolingOff.png')
COOLING_ON         = join(IMAGES_DIR, 'coolingOn.png')
PLAY_ICON          = join(IMAGES_DIR, 'play.png')
PAUSE_ICON         = join(IMAGES_DIR, 'pause.png')
SELECTED_LANG_ICON = join(IMAGES_DIR, 'downArrow.png')
LOCK_GIF           = join(IMAGES_DIR, 'lock.gif')
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
