## begin license ##
#
# Copyright (C) 2011-2014, 2020, 2023-2024 Seecr (Seek You Too B.V.) https://seecr.nl
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

from .app import main


def test_no_license(tmp_path):
    testdir = tmp_path / "testdir"
    testdir.mkdir()
    source_file = testdir / "source_file.py"
    source_file.write_text(
        """from sys import argv

def someMethod():
    return False
"""
    )
    conf_file = testdir / "applylicense.conf"
    conf_file.write_text(
        r"""{
    "project": "Some Project",
    "description": "This is just a dummy project for testing purposes.",
    "license": "arr",
    "copyrights": [
        {"name": "CQ2", "url": "http://cq2.nl"},
        {"name": "Seecr", "url": "http://seecr.nl",
         "text": "Some optional text"}
    ]
}
"""
    )

    main(["--year", "2042", conf_file.as_posix(), testdir.as_posix()])

    assert (
        source_file.read_text()
        == """## begin license ##
#
# This is just a dummy project for testing purposes.
#
# All rights reserved.
#
# Copyright (C) 2042 CQ2 http://cq2.nl
# Copyright (C) 2042 Seecr http://seecr.nl
#     Some optional text
#
# This file is part of "Some Project"
#
## end license ##

from sys import argv

def someMethod():
    return False
"""
    )
