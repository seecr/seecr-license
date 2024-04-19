## begin license ##
#
# Copyright (C) 2011-2012, 2020, 2023-2024 Seecr (Seek You Too B.V.) https://seecr.nl
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

from .license import License


def test_init_license():
    l = License(
        "some license template",
        project="some project",
        description="describing the project",
    )
    assert l._template == "some license template"
    assert l._project == "some project"
    assert l._description == "describing the project"


def test_license_from_file(tmp_path):
    license_file_path = tmp_path / "license.txt"
    license_file_path.write_text("license template")
    l = License.fromFile(
        license_file_path, project="some project", description="describing the project"
    )
    assert l._template == "license template"
    assert l._project == "some project"
    assert l._description == "describing the project"


def test_fill_license():
    l = License(
        """This is project: %(project)s.
%(description)s

%(copyrightlines)s
""",
        project="Seecr License",
        description="Some description.",
    )
    assert (
        l.fill(copyrightLines="""Copyright (C) 2009, 2011 Seecr http://seecr.nl""")
        == """
This is project: Seecr License.
Some description.

Copyright (C) 2009, 2011 Seecr http://seecr.nl
"""
    )


def test_fill_license_no_description():
    l = License(
        """All rights reserved.

%(copyrightlines)s
"""
    )
    assert (
        l.fill(copyrightLines="""Copyright (C) 2009, 2011 Seecr http://seecr.nl""")
        == """
All rights reserved.

Copyright (C) 2009, 2011 Seecr http://seecr.nl
"""
    )
