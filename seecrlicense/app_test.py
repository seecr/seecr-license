## begin license ##
#
# All rights reserved.
#
# Copyright (C) 2011-2014, 2020, 2023 Seecr (Seek You Too B.V.) https://seecr.nl
#
# This file is part of "Seecr Tools"
#
## end license ##

from .app import main

def test_no_license(tmp_path):
    testdir = tmp_path / 'testdir'
    testdir.mkdir()
    source_file = testdir / 'source_file.py'
    source_file.write_text("""from sys import argv

def someMethod():
    return False
""")
    conf_file = testdir / 'applylicense.conf'
    conf_file.write_text(r"""{
    "project": "Some Project",
    "description": "This is just a dummy project for testing purposes.",
    "license": "arr",
    "copyrights": [
        {"name": "CQ2", "url": "http://cq2.nl"},
        {"name": "Seecr", "url": "http://seecr.nl",
         "text": "Some optional text"}
    ]
}
""")

    main(['--year', '2042', conf_file.as_posix(), testdir.as_posix()])


    assert source_file.read_text() == """## begin license ##
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

