from os import system, path, mkdir, remove
from glob import glob
from sys import argv, exit

out_dir = 'out'

if not path.exists(out_dir):
    mkdir(out_dir)
else:
    assert path.isdir(out_dir)

dbg_flags = ''
if 'release' not in argv:
    #dbg_flags = '-g -fsanitize=address,undefined -fstack-protector-strong -D_FORTIFY_SOURCE=2'
    dbg_flags = '-g -fstack-protector-strong -D_FORTIFY_SOURCE=2'

r = system(rf'gcc main.c -o {out_dir}\maptor.exe libs\raylib\lib\libraylib.a -lopengl32 -lgdi32 -lwinmm -lkernel32 -luser32 -Wall -Wextra -Wpedantic -Werror {dbg_flags}')
exit(r)