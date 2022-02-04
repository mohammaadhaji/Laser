from distutils.dir_util import copy_tree
from pathlib import Path
import shutil, os

laser     = Path(__file__).parent.absolute()
parentDir = Path(laser).parent
cLaser    = os.path.join(parentDir, 'cLaser')


if os.path.isdir(cLaser):
    shutil.rmtree(cLaser)

os.mkdir(cLaser)
copy_tree(laser, cLaser)
os.chdir(cLaser)

files = []
for f in os.listdir(cLaser):
    if f.endswith('.py') and f != 'setup.py':
        files.append(os.path.join(cLaser, f))

for file in files:
    os.system(f'python -m nuitka --module --no-pyi-file {file}')

os.system('rm -rf *.py *.c *.build')
os.system('echo import app > main.py')