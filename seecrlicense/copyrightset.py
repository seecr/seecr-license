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

from io import StringIO
from textwrap import TextWrapper


class CopyrightSet(object):
    def __init__(self, copyrightDictList):
        self._mergeEquallyNamed(copyrightDictList)

    def _mergeEquallyNamed(self, copyrightDictList):
        self._copyrights = {}
        for c in copyrightDictList:
            matchC = self._copyrights.get(c['name'])
            if matchC is None:
                self._copyrights[c['name']] = cCopy = c.copy()
                cCopy['years'] = set(c['years'])
            else:
                if max(c['years']) >= max(matchC['years']):
                    matchC['url'] = c['url']
                    if 'text' in c:
                        matchC['text'] = c['text']
                    elif 'text' in matchC:
                        del matchC['text']
                matchC['years'].update(c['years'])

    def asCopyrightLines(self):
        s = StringIO()
        for copyright in sorted(list(self._copyrights.values()), key=lambda c: (min(c['years']), c['name'])):
            name = copyright['name']
            url = copyright['url']
            yearString = _serializeYears(copyright['years'])
            s.write(copyrightLineTemplate % locals())
            if copyright.get('text'):
                s.write(_textWrapper.fill(copyright['text']) + '\n')
        return s.getvalue()

    def merge(self, other):
        return CopyrightSet(list(self._copyrights.values()) + list(other._copyrights.values()))

    def __str__(self):
        return self.asCopyrightLines()

    def __eq__(self, other):
        return other.__class__ is self.__class__ and \
            self._copyrights == other._copyrights

def _serializeYears(years):
    intervals=[]
    for year in sorted(years):
        if len(intervals) == 0 or year > intervals[-1]['end'] + 1:
            intervals.append({'start': year})
        intervals[-1]['end'] = year
    return ', '.join(
        '-'.join(
            str(y)
            for y in sorted(set(interval.values()))
        )
        for interval in intervals
    )


copyrightLineTemplate = "\
Copyright (C) %(yearString)s %(name)s %(url)s\n"

_textWrapper = TextWrapper(width=79, initial_indent=4 * ' ', subsequent_indent=4 * ' ')

