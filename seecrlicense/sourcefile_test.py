## begin license ##
#
# Copyright (C) 2011-2013, 2017, 2020, 2023-2024 Seecr (Seek You Too B.V.) https://seecr.nl
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

import pytest

from os import chmod, stat
from os.path import join
from stat import ST_MODE
from time import localtime

from .sourcefile import (
    SourceFile,
    UnrecognizedFileType,
    _copyrightLineRe,
    CopyrightSet,
    C_MARKERS,
    HASH_MARKERS,
)
from .license import License


def test_python_markers(tmp_path):
    fp = tmp_path / "file.py"
    fp.write_text("")
    assert SourceFile(fp).licenseMarkers == HASH_MARKERS


def test_c_markers(tmp_path):
    for extension in ["c", "css", "js"]:
        fp = tmp_path / f"file.{extension}"
        fp.write_text("")
        assert SourceFile(fp).licenseMarkers == C_MARKERS


def test_markers_for_makefile(tmp_path):
    fp = tmp_path / "Makefile"
    fp.write_text("")
    assert SourceFile(fp).licenseMarkers == HASH_MARKERS


def test_markers_based_on_hash_bang(tmp_path):
    fp = tmp_path / "start-script"
    fp.write_text("#!/bin/bash\necho hello")
    assert SourceFile(fp).licenseMarkers == HASH_MARKERS


def test_markers_not_defined(tmp_path):
    for name in ["file.xxx", ".Makefile"]:
        fp = tmp_path / name
        fp.write_text("")
        with pytest.raises(UnrecognizedFileType) as exc_info:
            SourceFile(fp)
        assert (
            str(exc_info.value)
            == f"{fp.as_posix()} is not recognized as a source file."
        )


def test_binary_file(tmp_path):
    fp = tmp_path / "binary"
    fp.write_bytes(bytes(range(256)))
    pytest.raises(UnrecognizedFileType, SourceFile, fp)


def test_find_markers(tmp_path):
    fp = tmp_path / "file.py"
    fp.write_text(
        """#!/usr/bin/env python2

_## begin license ##
#
# LICENSE TEXT
#
_## end license ##

def code(here): pass""".replace(
            "_#", "#"
        )
    )
    assert SourceFile(fp).findMarkerIndexes() == (2, 7)


def test_find_markers_no_license(tmp_path):
    fp = tmp_path / "file.py"
    fp.write_text(
        """#!/usr/bin/env python2

def code(here): pass"""
    )
    assert SourceFile(fp).findMarkerIndexes() == (1, 1)


def test_parse_copyright_lines(tmp_path):
    lastYear = localtime().tm_year - 1
    dummySource = tmp_path / "dummy.py"
    dummySource.write_text("ignored")

    sourceFile = SourceFile(dummySource)
    sourceFile._readLicenseLines = lambda: [
        "    Copyright (C) %s Seecr http://www.seecr.nl" % lastYear
    ]
    assert sourceFile._parseCopyrightLines() == [
        {"name": "Seecr", "years": {lastYear}, "url": "http://www.seecr.nl"}
    ]

    sourceFile._readLicenseLines = lambda: [
        "    Copyright (C) 2003,2007-2009, 2011 Seecr http://www.seecr.nl"
    ]
    assert sourceFile._parseCopyrightLines() == [
        {
            "name": "Seecr",
            "years": {2003, 2007, 2008, 2009, 2011},
            "url": "http://www.seecr.nl",
        }
    ]

    sourceFile._readLicenseLines = lambda: [
        "    Copyright (C) 2003,2007-2009, 2011 Seecr http://www.seecr.nl",
        "        text1",
        "        text2",
    ]
    assert sourceFile._parseCopyrightLines() == [
        {
            "name": "Seecr",
            "years": {2003, 2007, 2008, 2009, 2011},
            "url": "http://www.seecr.nl",
            "text": "text1 text2",
        }
    ]


def test_copyright_line_re(tmp_path):
    assert _copyrightLineRe.match(
        "         Copyright (C) 2003  The Esteemed Client  http://theesteemedclient.com"
    ).groupdict() == {
        "years": "2003",
        "name": "The Esteemed Client",
        "url": "http://theesteemedclient.com",
        "text": None,
    }
    assert _copyrightLineRe.match(
        "Copyright (C) 2003,2005-2007, 2010  The Esteemed Client  http://theesteemedclient.com  text1\ntext2\n   text3"
    ).groupdict() == {
        "years": "2003,2005-2007, 2010",
        "name": "The Esteemed Client",
        "url": "http://theesteemedclient.com",
        "text": "text1\ntext2\n   text3",
    }
    assert _copyrightLineRe.match(
        "Copyright (C) 2001 2QC  http://2qc.nl"
    ).groupdict() == {
        "years": "2001",
        "name": "2QC",
        "url": "http://2qc.nl",
        "text": None,
    }
    assert _copyrightLineRe.match(
        "Copyright (C) 2016 SURFmarket https://surf.nl"
    ).groupdict() == {
        "years": "2016",
        "name": "SURFmarket",
        "url": "https://surf.nl",
        "text": None,
    }


def test_update_license_keeps_stats(tmp_path):
    dummySource = tmp_path / "dummy.py"
    dummySource.write_text("ignored")
    dummySource.chmod(0o777)
    originalStat = dummySource.stat()

    sourceFile = SourceFile(dummySource)
    sourceFile._updateLicense(License("Ignored"), CopyrightSet([]))
    newStat = dummySource.stat()
    assert newStat.st_mode == originalStat.st_mode


def test_force_update(tmp_path):
    cs = CopyrightSet(
        [{"years": [2006], "name": "Past Inc.", "url": "http://past.url"}]
    )

    updateCalled = []

    dummySource = tmp_path / "dummy.py"
    dummySource.write_text(
        """## begin license ##
#
# All rights reserved.
#
# %s
#
## end license ##
"""
        % cs.asCopyrightLines()
    )

    sourceFile = SourceFile(dummySource)

    def _updateLicense(*args, **kwargs):
        updateCalled.append(True)

    sourceFile._updateLicense = _updateLicense

    sourceFile.maybeUpdateLicense("DUMMY LICENSE", cs)
    assert updateCalled == []
    sourceFile.maybeUpdateLicense("DUMMY LICENSE", cs, forceUpdate=True)
    assert updateCalled == [True]
