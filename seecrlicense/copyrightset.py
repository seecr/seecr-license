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

from io import StringIO
from textwrap import TextWrapper


class CopyrightSet(object):
    def __init__(self, copyrightDictList):
        self._mergeEquallyNamed(copyrightDictList)

    def _mergeEquallyNamed(self, copyrightDictList):
        self._copyrights = {}
        for c in copyrightDictList:
            matchC = self._copyrights.get(c["name"])
            if matchC is None:
                self._copyrights[c["name"]] = cCopy = c.copy()
                cCopy["years"] = set(c["years"])
            else:
                if max(c["years"]) >= max(matchC["years"]):
                    matchC["url"] = c["url"]
                    if "text" in c:
                        matchC["text"] = c["text"]
                    elif "text" in matchC:
                        del matchC["text"]
                matchC["years"].update(c["years"])

    def asCopyrightLines(self):
        s = StringIO()
        for copyright in sorted(
            list(self._copyrights.values()), key=lambda c: (min(c["years"]), c["name"])
        ):
            name = copyright["name"]
            url = copyright["url"]
            yearString = _serializeYears(copyright["years"])
            s.write(copyrightLineTemplate % locals())
            if copyright.get("text"):
                s.write(_textWrapper.fill(copyright["text"]) + "\n")
        return s.getvalue()

    def merge(self, other):
        return CopyrightSet(
            list(self._copyrights.values()) + list(other._copyrights.values())
        )

    def __str__(self):
        return self.asCopyrightLines()

    def __eq__(self, other):
        return (
            other.__class__ is self.__class__ and self._copyrights == other._copyrights
        )


def _serializeYears(years):
    intervals = []
    for year in sorted(years):
        if len(intervals) == 0 or year > intervals[-1]["end"] + 1:
            intervals.append({"start": year})
        intervals[-1]["end"] = year
    return ", ".join(
        "-".join(str(y) for y in sorted(set(interval.values())))
        for interval in intervals
    )


copyrightLineTemplate = "\
Copyright (C) %(yearString)s %(name)s %(url)s\n"

_textWrapper = TextWrapper(width=79, initial_indent=4 * " ", subsequent_indent=4 * " ")
