from pathlib import Path
from os.path import join


CURRENT_FILE_DIR = Path(__file__).parent.absolute()
APP_UI = join(CURRENT_FILE_DIR, 'ui/ui.ui')
USERS_DIR = join(CURRENT_FILE_DIR, 'users')
CASES_DIR = join(CURRENT_FILE_DIR, 'cases')
TUTORIALS_DIR = join(CURRENT_FILE_DIR, 'tutorials')
EDIT_ICON = join(CURRENT_FILE_DIR, 'ui/images/edit.png')
WATERCIRCULATION = join(CURRENT_FILE_DIR, 'ui/images/waterCirculation.png')
WATERCIRCULATIONWARNING = join(CURRENT_FILE_DIR, 'ui/images/waterCirculationWarning.png')
TEMP = join(CURRENT_FILE_DIR, 'ui/images/temp.png')
TEMPWARNING = join(CURRENT_FILE_DIR, 'ui/images/tempWarning.png')
WATERLEVEL = join(CURRENT_FILE_DIR, 'ui/images/waterLevel.png')
WATERLEVELWARNING = join(CURRENT_FILE_DIR, 'ui/images/waterLevelWarning.png')
LOCK = join(CURRENT_FILE_DIR, 'ui/images/lock.png')
UNLOCK = join(CURRENT_FILE_DIR, 'ui/images/unlock.png')
COOLING_OFF = join(CURRENT_FILE_DIR, 'ui/images/coolingOff.png')
COOLING_ON = join(CURRENT_FILE_DIR, 'ui/images/coolingOn.png')
BODY_PART_ICONS = {
    'f face': join(CURRENT_FILE_DIR, 'ui/images/fFace'),
    'f armpit': join(CURRENT_FILE_DIR, 'ui/images/fArmpit'),
    'f arm': join(CURRENT_FILE_DIR, 'ui/images/fArm'),
    'f body': join(CURRENT_FILE_DIR, 'ui/images/fBody'),
    'f bikini': join(CURRENT_FILE_DIR, 'ui/images/fBikini'),
    'f leg': join(CURRENT_FILE_DIR, 'ui/images/fLeg'),
    'm face': join(CURRENT_FILE_DIR, 'ui/images/mFace'),
    'm armpit': join(CURRENT_FILE_DIR, 'ui/images/mArmpit'),
    'm arm': join(CURRENT_FILE_DIR, 'ui/images/mArm'),
    'm body': join(CURRENT_FILE_DIR, 'ui/images/mBody'),
    'm bikini': join(CURRENT_FILE_DIR, 'ui/images/mBikini'),
    'm leg': join(CURRENT_FILE_DIR, 'ui/images/mLeg')
}
PLAY_ICON = join(CURRENT_FILE_DIR, 'ui/images/play.png')
PAUSE_ICON = join(CURRENT_FILE_DIR, 'ui/images/pause.png')
