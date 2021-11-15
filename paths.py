from pathlib import Path
from os.path import join


CURRENT_FILE_DIR = Path(__file__).parent.absolute()
APP_UI = join(CURRENT_FILE_DIR, 'ui/ui.ui')
USERS_DIR = join(CURRENT_FILE_DIR, 'users')
EDIT_ICON = join(CURRENT_FILE_DIR, 'ui/images/edit.png')
WATERCIRCULATION = join(CURRENT_FILE_DIR, 'ui/images/waterCirculation.png')
WATERCIRCULATIONWARNING = join(CURRENT_FILE_DIR, 'ui/images/waterCirculationWarning.png')
TEMP = join(CURRENT_FILE_DIR, 'ui/images/temp.png')
TEMPWARNING = join(CURRENT_FILE_DIR, 'ui/images/tempWarning.png')
WATERLEVEL = join(CURRENT_FILE_DIR, 'ui/images/waterLevel.png')
WATERLEVELWARNING = join(CURRENT_FILE_DIR, 'ui/images/waterLevelWarning.png')
LOCK = join(CURRENT_FILE_DIR, 'ui/images/lock.png')
UNLOCK = join(CURRENT_FILE_DIR, 'ui/images/unlock.png')