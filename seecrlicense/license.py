# -*- coding: utf-8 -*-
## begin license ##
#
# Copyright (C) 2011-2012, 2014, 2020, 2023-2024 Seecr (Seek You Too B.V.) https://seecr.nl
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

BEGIN_LICENSE_TEXT = '%s begin license %s\n'
END_LICENSE_TEXT = '%s end license %s\n'

class License(object):
    def __init__(self, template, project=None, description=None):
        self._template = template
        self._project = project
        self._description = description

    @classmethod
    def fromFile(cls, filePath, project=None, description=None):
        with open(filePath) as f:
            return License(f.read().strip(), project=project, description=description)

    def fill(self, copyrightLines):
        substitutionDict = dict(
            (key, value or '')
            for key, value in [
                ('project', self._project),
                ('description', self._description),
                ('copyrightlines', copyrightLines)
            ]
        )
        return "\n%s\n" % (self._template % substitutionDict).strip("\n")

