## begin license ##
#
# "Seecr Tools" provides tools for git, ssh, nginx etc. It makes life easier for Seecr developers.
#
# All rights reserved.
#
# Copyright (C) 2011-2012, 2020, 2023 Seecr (Seek You Too B.V.) https://seecr.nl
#
# This file is part of "Seecr Tools"
#
## end license ##

from .license import License

def test_init_license():
    l = License("some license template", project="some project", description="describing the project")
    assert l._template == "some license template"
    assert l._project == "some project"
    assert l._description == "describing the project"

def test_license_from_file(tmp_path):
    license_file_path = tmp_path/'license.txt'
    license_file_path.write_text("license template")
    l = License.fromFile(license_file_path, project="some project", description="describing the project")
    assert l._template == "license template"
    assert l._project == "some project"
    assert l._description == "describing the project"

def test_fill_license():
    l = License("""This is project: %(project)s.
%(description)s

%(copyrightlines)s
""", project='Seecr License', description='Some description.')
    assert l.fill(copyrightLines="""Copyright (C) 2009, 2011 Seecr http://seecr.nl""") == """
This is project: Seecr License.
Some description.

Copyright (C) 2009, 2011 Seecr http://seecr.nl
"""

def test_fill_license_no_description():
    l = License("""All rights reserved.

%(copyrightlines)s
""")
    assert l.fill(copyrightLines="""Copyright (C) 2009, 2011 Seecr http://seecr.nl""") == """
All rights reserved.

Copyright (C) 2009, 2011 Seecr http://seecr.nl
"""



