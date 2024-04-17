## begin license ##
#
# "Seecr Tools" provides tools for git, ssh, nginx etc. It makes life easier for Seecr developers.
#
# All rights reserved.
#
# Copyright (C) 2011-2013, 2016-2017, 2020, 2023 Seecr (Seek You Too B.V.) https://seecr.nl
#
# This file is part of "Seecr Tools"
#
## end license ##



from os import rename
from os.path import abspath, splitext, basename
from shutil import copystat
from re import compile, DOTALL

from .copyrightset import CopyrightSet


HASH_MARKERS = ('## begin license ##', '## end license ##', '# ')
C_MARKERS = ('/* begin license *', ' * end license */', ' * ')
markersByExtension = {
    '.c': C_MARKERS,
    '.cpp': C_MARKERS,
    '.css': C_MARKERS,
    '.scss': C_MARKERS,
    '.h': C_MARKERS,
    '.java': C_MARKERS,
    '.js': C_MARKERS,
    '.php': HASH_MARKERS,
    '.py': HASH_MARKERS,
    '.pyx': HASH_MARKERS,
    '.rules': HASH_MARKERS,
    '.sf': HASH_MARKERS,
    '.sh': HASH_MARKERS,
}
markersByFilename = {
    'Makefile': HASH_MARKERS
}

def _licenseMarkersForType(filename):
    ignored, fileExt = splitext(filename)
    return markersByExtension.get(fileExt) or markersByFilename.get(basename(filename))

def _licenseMarkersFromContent(filename):
    with open(filename, 'rb') as f:
        try:
            for i, line in enumerate(f):
                if i > 5:
                    break
                if line.startswith(b'#!'):
                    return HASH_MARKERS
        except UnicodeDecodeError:
            print("Error in: " + filename)
            raise

class UnrecognizedFileType(Exception):
    pass

class SourceFile(object):
    def __init__(self, filename):
        self.licenseMarkers = _licenseMarkersForType(filename) or _licenseMarkersFromContent(filename)
        if self.licenseMarkers is None:
            raise UnrecognizedFileType("%s is not recognized as a source file." % filename)
        self.licenseStartMarker, self.licenseEndMarker, self.licenseLineMarker = self.licenseMarkers
        self._filename = abspath(filename)
        with open(filename) as f:
            self._lines = f.read().split('\n')

    def maybeUpdateLicense(self, license, configuredCopyrightSet, forceUpdate=False, dryRun=False):
        copyrightLines = self._parseCopyrightLines()
        currentCopyrightSet = CopyrightSet(copyrightLines)
        mergedCopyrightSet = currentCopyrightSet.merge(configuredCopyrightSet)
        if mergedCopyrightSet != currentCopyrightSet or forceUpdate:
            self._updateLicense(license, mergedCopyrightSet, dryRun)

    def _updateLicense(self, license, copyrightSet, dryRun=False):
        if not dryRun:
            template = '\n'.join([
                self.licenseStartMarker,
                "%s",
                self.licenseEndMarker,
                ""])

            appliedLicense = license.fill(copyrightLines=copyrightSet.asCopyrightLines())
            contents = '\n'.join(self.licenseLineMarker + l for l in appliedLicense.split('\n'))
            formattedLines = (l.rstrip() for l in (template % contents).split('\n'))

            startMarkerIndex, endMarkerIndex = self.findMarkerIndexes()
            newLines = self._lines[:]
            newLines[startMarkerIndex:endMarkerIndex + 1] = formattedLines
            self._write(newLines)
        print("Updated %s" % self._filename)

    def _write(self, newLines):
        tmpFileName = self._filename + '.tmp'
        with open(tmpFileName, 'w') as tmpFile:
            copystat(self._filename, tmpFileName)
            tmpFile.write('\n'.join(newLines))
        rename(tmpFileName, self._filename)
        self._lines = newLines

    def _parseCopyrightLines(self):
        copyrightIndent = 0
        copyrightLines = []
        for line in self._readLicenseLines():
            indent = len(line) - len(line.lstrip())
            line = line.strip()
            if line.startswith("Copyright (C)"):
                copyrightLines.append(line)
                copyrightIndent = indent
            elif copyrightLines:
                if indent > copyrightIndent:
                    copyrightLines[-1] += ' ' + line
                elif line == "":
                    break
        return [self._parseCopyrightLine(crl) for crl in copyrightLines]

    def _readLicenseLines(self):
        startMarkerIndex, endMarkerIndex = self.findMarkerIndexes()
        licenseLines = []
        if startMarkerIndex != endMarkerIndex:
            lineMarkerLength = len(self.licenseLineMarker)
            licenseLines = [line[lineMarkerLength:] for line in self._lines[startMarkerIndex + 2:endMarkerIndex - 1]]
        return licenseLines

    def _parseCopyrightLine(self, line):
        m = _copyrightLineRe.match(line)
        copyrightAttributes = m.groupdict()
        if copyrightAttributes['text'] is None:
            del copyrightAttributes['text']
        years = set()
        for y in (y.strip() for y in copyrightAttributes['years'].split(',')):
            if '-' in y:
                left, right = y.split('-')
                years.update(range(int(left), int(right) + 1))
            else:
                years.add(int(y))
        copyrightAttributes['years'] = set(years)
        return copyrightAttributes

    def findMarkerIndexes(self):
        startMarkerIndex = -1
        endMarkerIndex = -1
        for index, line in enumerate(self._lines):
            line = line.rstrip()
            if startMarkerIndex < 0:
                if line == self.licenseStartMarker:
                    startMarkerIndex = index
            if line == self.licenseEndMarker:
                endMarkerIndex = index
                try:
                    if self._lines[index + 1].strip() == '':
                        endMarkerIndex = index + 1
                except IndexError:
                    pass
                break

        if startMarkerIndex < 0:
            if endMarkerIndex < 0:
                return self._findInsertionPoint()
            raise RuntimeError("'end license' marker found without matching 'begin license' in file %s" % self._filename)
        elif endMarkerIndex < 0:
            raise RuntimeError("'begin license' marker found without matching 'end license' in file %s" % self._filename)

        return (startMarkerIndex, endMarkerIndex)

    def _findInsertionPoint(self):
        insertionPoint = 0
        line = self._lines[insertionPoint]
        if line.startswith("#!") or line.startswith('<?php'):
            insertionPoint += 1
        line = self._lines[insertionPoint]
        if self._isEncodingLine(line):
            insertionPoint += 1
        insertionPointEnd = insertionPoint
        if self._lines[insertionPointEnd].strip() == '':
            insertionPointEnd += 1
        return (insertionPoint, insertionPointEnd - 1)

    def _isEncodingLine(self, line):
        """See http://www.python.org/dev/peps/pep-0263"""
        return line.startswith('#') and ('coding:' in line or 'coding=' in line)


_yearPart = r"(?P<years>\d{4}((-|,\s*)\d{4})*)"
_namePart = r"(?P<name>\S.*\S)"
_urlPart = r"(?P<url>http(?:s)?://\S+)"
_optionalTextPart = r"(\s+(?P<text>.+))?"
_copyrightLineRe = compile(r"^\s*Copyright \(C\)\s+" + _yearPart + r"\s+" + _namePart + r"\s+" + _urlPart + _optionalTextPart + "$", DOTALL)
