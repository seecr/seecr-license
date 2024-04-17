## begin license ##
#
# Copyright (C) 2007, 2009, 2017 CQ2 http://cq2.nl
# Copyright (C) 2011-2014, 2016-2017, 2020-2024 Seecr (Seek You Too B.V.) https://seecr.nl
# Copyright (C) 2012 Seek You Too http://cq2.nl
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

from .applylicense import ApplyLicense

import json
import pytest

def test_apply_license_to_file_without_one(tmp_path):
    applyLicense = ApplyLicense(ApplyLicense.Config({
        'project': 'Some Project',
        'license': 'arr',
        'copyrights': [
            {'name': 'CQ2', 'url': 'http://cq2.nl'},
        ]

    }), year="2007", changedOnly=False)

    sourceFile = tmp_path / 'source.py'
    sourceFile.write_text("# stuff")

    applyLicense.run([sourceFile])

    result = sourceFile.read_text()
    assert result == """\
_## begin license ##
#
# All rights reserved.
#
# Copyright (C) 2007 CQ2 http://cq2.nl
#
# This file is part of "Some Project"
#
_## end license ##

# stuff""".replace('_#', '#')

    sourceFile = tmp_path / 'source.sh'
    sourceFile.write_text("""#!/usr/bin/env python2

# stuff""")

    applyLicense.run([sourceFile])

    result = sourceFile.read_text()
    assert result == """\
#!/usr/bin/env python2
_## begin license ##
#
# All rights reserved.
#
# Copyright (C) 2007 CQ2 http://cq2.nl
#
# This file is part of "Some Project"
#
_## end license ##

# stuff""".replace('_#', '#')

def test_run_corrupt_original_license(tmp_path):
    applyLicense = ApplyLicense(ApplyLicense.Config({
        'project': 'Some Project',
        'description': 'This is just a\ndummy project\nfor testing purposes.',
        'license': 'arr',
        'copyrights': [
            {'name': 'CQ2', 'url': 'http://cq2.nl', 'years': [2007, 2009]},
        ]

    }), changedOnly=False)

    sourceFile = tmp_path / 'source.py'
    sourceFile.write_text("## begin license ##\n# \n# stuff")
    with pytest.raises(RuntimeError) as e:
        applyLicense.run([sourceFile])
    assert str(e.value) == "'begin license' marker found without matching 'end license' in file %s" % sourceFile

    sourceFile.write_text("#\n## end license ##\n# stuff")
    with pytest.raises(RuntimeError) as e:
        applyLicense.run([sourceFile])
    assert str(e.value) == "'end license' marker found without matching 'begin license' in file %s" % sourceFile


def test_apply_license_to_file_with_copyright_lines(tmp_path):
    conf_path = tmp_path / 'license.conf'
    conf_path.write_text(json.dumps({
            "project": "Seecr License",
            "description": "\"Seecr License\" is a tool to insert licenses into files.",
            "copyrights": [{"name": "Seek You Too", "url": "http://cq2.nl"}],
            "license": "arr"}))

    applyLicense = ApplyLicense.fromFile(conf_path, year='2012', changedOnly=False)

    src_path = tmp_path / 'src'
    src_path.mkdir()

    (src_path / 'file.py').write_text("""
# some comment

_## begin license ##
#
# Our favourite license: use only for things we like.
#
# Copyright (C) 2010, 2011 Seek You Too http://seekyoutoo.nl
#     Extra text
#
_## end license ##

def f(x): pass""".replace('_#', '#'))

    applyLicense.run(paths=[src_path])

    assert (src_path / 'file.py').read_text() == """
# some comment

_## begin license ##
#
# "Seecr License" is a tool to insert licenses into files.
#
# All rights reserved.
#
# Copyright (C) 2010-2012 Seek You Too http://cq2.nl
#
# This file is part of "Seecr License"
#
_## end license ##

def f(x): pass""".replace('_#', '#')


def test_apply_gplv2(tmp_path):
    applyLicense = ApplyLicense(ApplyLicense.Config({
        'project': 'Some Project',
        'description': 'This is just a\ndummy project\nfor testing purposes.',
        'license': 'GPLv2',
        'copyrights': [
            {'name': 'CQ2', 'url': 'http://cq2.nl'},
        ]

    }), year=2034, changedOnly=False)

    sourceFile = tmp_path / 'source.py'
    sourceFile.write_text("# stuff")

    applyLicense.run([sourceFile])

    result = sourceFile.read_text()
    assert "Some Project" in result
    assert "dummy project" in result
    assert "2034" in result
    assert "GNU General Public License" in result

def test_jinja2(tmp_path):
    applyLicense = ApplyLicense(ApplyLicense.Config({
        'project': 'Some Project',
        'description': 'This is just a dummy project for testing purposes.',
        'license': 'arr',
        'copyrights': {'seecr': {'name': 'Seecr', 'url': 'https://seecr.nl'}}
    }), year="2024", changedOnly=False)

    sourceFile = tmp_path / 'source.j2'
    sourceFile.write_text("{{ 'hello' }}")

    applyLicense.run([sourceFile])

    assert sourceFile.read_text() == """\
{# begin license ##
#
# This is just a dummy project for testing purposes.
#
# All rights reserved.
#
# Copyright (C) 2024 Seecr https://seecr.nl
#
# This file is part of "Some Project"
#
## end license #}

{{ 'hello' }}"""

def test_php(tmp_path):
    applyLicense = ApplyLicense(ApplyLicense.Config({
        'project': 'Some Project',
        'description': 'This is just a dummy project for testing purposes.',
        'license': 'arr',
        'copyrights': [
            {'name': 'CQ2', 'url': 'http://cq2.nl'},
        ]

    }), year="2007", changedOnly=False, select='seecr')

    sourceFile = tmp_path / 'source.php'
    sourceFile.write_text("<?php\n?>")

    applyLicense.run([sourceFile])

    assert sourceFile.read_text() == """\
<?php
_## begin license ##
#
# This is just a dummy project for testing purposes.
#
# All rights reserved.
#
# Copyright (C) 2007 CQ2 http://cq2.nl
#
# This file is part of "Some Project"
#
_## end license ##

?>""".replace('_#', '#')


def test_new_style_config(tmp_path):
    applyLicense = ApplyLicense(ApplyLicense.Config({
        'project': 'Some Project',
        'description': 'This is just a dummy project for testing purposes.',
        'license': 'arr',
        'copyrights': {
            'cq2': {'name': 'CQ2', 'url': 'http://cq2.nl'},
            'seecr': {'name': 'Seecr', 'url': 'https://seecr.nl'},
            'other': {'name': 'Example', 'url': 'https://example.org'},
        }

    }), year="2007", changedOnly=False, select='seecr,cq2')

    sourceFile = tmp_path / 'source.py'
    sourceFile.write_text("#\ndef main():\n    pass\n")

    applyLicense.run([sourceFile])

    assert sourceFile.read_text() == """\
_## begin license ##
#
# This is just a dummy project for testing purposes.
#
# All rights reserved.
#
# Copyright (C) 2007 CQ2 http://cq2.nl
# Copyright (C) 2007 Seecr https://seecr.nl
#
# This file is part of "Some Project"
#
_## end license ##

#
def main():
    pass
""".replace('_#', '#')


def test_new_style_config2(tmp_path):
    applyLicense = ApplyLicense(ApplyLicense.Config({
        'project': 'Some Project',
        'description': 'This is just a dummy project for testing purposes.',
        'license': 'arr',
        'copyrights': {
            'cq2': {'name': 'CQ2', 'url': 'http://cq2.nl'},
            'seecr': {'name': 'Seecr', 'url': 'https://seecr.nl'},
            'other': {'name': 'Example', 'url': 'https://example.org'},
        }

    }), year="2007", changedOnly=False)

    sourceFile = tmp_path / 'source.py'
    sourceFile.write_text("#\ndef main():\n    pass\n")

    applyLicense.run([sourceFile])

    assert sourceFile.read_text() == """\
_## begin license ##
#
# This is just a dummy project for testing purposes.
#
# All rights reserved.
#
# Copyright (C) 2007 Seecr https://seecr.nl
#
# This file is part of "Some Project"
#
_## end license ##

#
def main():
    pass
""".replace('_#', '#')


def test_skip_path(tmp_path, capsys):
    applyLicense = ApplyLicense(ApplyLicense.Config({
        'project': 'Some Project',
        'description': 'This is just a\ndummy project\nfor testing purposes.',
        'license': 'arr',
        'copyrights': [
            {'name': 'CQ2', 'url': 'http://cq2.nl'},
        ]

    }), changedOnly=False)

    sourceFile = tmp_path/ 'source.unknown'
    sourceFile.write_text("# stuff")

    applyLicense.run([sourceFile])

    assert f'Skipped {sourceFile.as_posix()!r}' in capsys.readouterr().out


def test_skip_path_does_not_exist(tmp_path, capsys):
    applyLicense = ApplyLicense(ApplyLicense.Config({
        'project': 'Some Project',
        'description': 'This is just a\ndummy project\nfor testing purposes.',
        'license': 'arr',
        'copyrights': [
            {'name': 'CQ2', 'url': 'http://cq2.nl'},
        ]

    }), changedOnly=False)

    sourceFile = tmp_path / 'doesnotexist.py'

    applyLicense.run([sourceFile])

    assert f'Skipped {sourceFile.as_posix()!r}' in capsys.readouterr().out


def test_should_skip_dot_git_directory(tmp_path, capsys):
    applyLicense = ApplyLicense(ApplyLicense.Config({
        'project': 'Some Project',
        'description': 'This is just a\ndummy project\nfor testing purposes.',
        'license': 'arr',
        'copyrights': [
            {'name': 'CQ2', 'url': 'http://cq2.nl'},
        ]
    }), changedOnly=False)

    projectPath = tmp_path/'project_dir'
    script1 = projectPath/'.git'/'somewhere'/'bash-script'
    script1.parent.mkdir(parents=True)
    script1.write_text("#!/bin/bash\n")
    pyenvpath = projectPath/'python-env'
    script2 = pyenvpath/'bin'/'bash-script'
    script2.parent.mkdir(parents=True)
    script2.write_text("#!/bin/bash\n")
    (pyenvpath/'pyvenv.cfg').write_text('config = true\n')

    applyLicense.run([str(projectPath)])

    skipped = {l.strip() for l in capsys.readouterr().out.split('\n') if l.strip().startswith('Skipped')}
    assert skipped == {"Skipped '.git'", "Skipped 'python-env'"}
    assert script1.read_text() == "#!/bin/bash\n"
    assert script2.read_text() == "#!/bin/bash\n"

