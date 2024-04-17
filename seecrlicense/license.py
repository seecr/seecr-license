# -*- coding: utf-8 -*-
## begin license ##
#
# "Seecr Tools" provides tools for git, ssh, nginx etc. It makes life easier for Seecr developers.
#
# All rights reserved.
#
# Copyright (C) 2011-2012, 2014, 2020, 2023 Seecr (Seek You Too B.V.) https://seecr.nl
#
# This file is part of "Seecr Tools"
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

