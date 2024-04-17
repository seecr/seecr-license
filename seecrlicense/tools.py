## begin license ##
#
# Copyright (C) 2024 Seecr (Seek You Too B.V.) https://seecr.nl
#
# This file is part of "Seecr License"
#
# "Seecr License" is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# "Seecr License" is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with "Seecr License"; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
#
## end license ##

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
