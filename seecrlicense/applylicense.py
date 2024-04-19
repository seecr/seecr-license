## begin license ##
#
# Copyright (C) 2011-2014, 2017, 2020-2024 Seecr (Seek You Too B.V.) https://seecr.nl
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

from os import walk, listdir
from os.path import isfile, isdir, join, basename
from .license import License
from .sourcefile import SourceFile, UnrecognizedFileType
from .copyrightset import CopyrightSet
from time import strftime, localtime
from .tools import git_status

import json
import pathlib
import importlib.resources as resources

license_path = resources.files("seecrlicense") / "license-data"

licenses = {f.stem: f for f in license_path.glob("*.header")}

IGNORED_DIRECTORIES = [".git", ".svn", "deps.d", "__pycache__"]

currentYear = strftime("%Y", localtime())


class ApplyLicense:
    def __init__(
        self, config, forceUpdate=False, changedOnly=True, dryRun=False, **kwargs
    ):
        self.license = config.license
        self.configuredCopyrights = config.copyrightSet(**kwargs)
        self._forceUpdate = forceUpdate
        self._changedOnly = changedOnly
        self._dryRun = dryRun

    @classmethod
    def fromFile(cls, configPath, **kwargs):
        return cls(
            cls.Config(json.loads(pathlib.Path(configPath).read_text())), **kwargs
        )

    def run(self, paths):
        if self._changedOnly is True:
            changes = git_status(fullPath=True)
            paths = [
                p for status, paths in changes.items() if "M" in status for p in paths
            ]

        for path in paths:
            if isfile(path):
                try:
                    self._maybeUpdateLicense(path)
                except UnrecognizedFileType:
                    print("Skipped '%s', filetype not recognized." % path)
            elif isdir(path):
                for curdir, subdirs, files in walk(path):
                    if should_skip_dir(curdir, files):
                        print("Skipped '%s'" % basename(curdir))
                        del subdirs[:]
                        continue

                    for file in files:
                        if file.startswith(".") and file.endswith(".swp"):
                            continue
                        try:
                            self._maybeUpdateLicense(join(curdir, file))
                        except UnrecognizedFileType:
                            continue
            else:
                print(
                    "Skipped '%s', it can not be recognized as either a file or a directory."
                    % path
                )

    def _maybeUpdateLicense(self, filepath):
        sf = SourceFile(filepath)
        print("Examining %s" % filepath)
        sf.maybeUpdateLicense(
            self.license,
            self.configuredCopyrights,
            forceUpdate=self._forceUpdate,
            dryRun=self._dryRun,
        )

    class Config:
        def __init__(self, configDict):
            license_path = _getLicenseFile(configDict["license"])
            self.license = License.fromFile(
                license_path,
                project=configDict.get("project"),
                description=configDict.get("description"),
            )
            self._copyrightsSelected = []
            self._copyrights = {}
            copyrights = configDict["copyrights"]
            if isinstance(copyrights, list):
                for copyrightset in configDict["copyrights"]:
                    copyrightset.pop("years", None)
                    self._copyrightsSelected.append(copyrightset)
            else:
                self._copyrights.update(copyrights)

        def copyrightSet(self, year=None, select=None, **_):
            year = int(year or currentYear)
            selected = self._copyrightsSelected[:]
            if not selected:
                for key in (
                    ["seecr"]
                    if select is None
                    else [s.strip() for s in select.split(",") if s.strip()]
                ):
                    selected.append(self._copyrights[key])
            if not selected:
                raise ValueError("No copyrights configured")
            return CopyrightSet([dict(c, years=[year]) for c in selected])


def _getLicenseFile(licenseType):
    license_path = licenses.get(licenseType)
    if license_path:
        print(f"Using license {licenseType}")
        return license_path
    raise KeyError("No such license: %s" % licenseType)


def should_skip_dir(curdir, files):
    return basename(curdir) in IGNORED_DIRECTORIES or "pyvenv.cfg" in files
