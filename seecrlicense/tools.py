
from os.path import join
from subprocess import Popen, PIPE

def git_status(fullPath=False):
    with Popen(["git", "status", "--porcelain"], stdout=PIPE, stderr=PIPE) as proc:
        stdout, stderr = proc.communicate()
        changes = {}
        _project_root = project_root()
        filename_fixup = lambda fn: join(_project_root, fn) if fullPath else fn

        for k, v in ((line[:2], line[2:].strip()) for line in stdout.decode(sys.stdout.encoding).split("\n") if line):
            changes.setdefault(k, []).append(filename_fixup(v))
        return changes
