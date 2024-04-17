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


from .copyrightset import CopyrightSet, _serializeYears

def test_as_copyright_lines():
    copyrightSet = CopyrightSet([
        {'years': [2009, 2011], 'name': 'Seecr', 'url': 'http://seecr.nl', 'text': 'some optional text' + 10 * " and some more"},
        {'years': [2007, 2009, 2008], 'name': 'Seek You Too', 'url': 'http://cq2.nl'},
    ])

    assert copyrightSet.asCopyrightLines() == "\
Copyright (C) 2007-2009 Seek You Too http://cq2.nl\n\
Copyright (C) 2009, 2011 Seecr http://seecr.nl\n\
    some optional text and some more and some more and some more and some more\n\
    and some more and some more and some more and some more and some more and\n\
    some more\n\
"

def test_equals():
    copyrightSet1 = CopyrightSet([
        {'years': [2011, 2009], 'name': 'Seecr', 'url': 'http://seecr.nl', 'text': 'some optional text' + 10 * " and some more"},
        {'years': [2007, 2009, 2008], 'name': 'Seek You Too', 'url': 'http://cq2.nl'},
    ])

    copyrightSet2 = CopyrightSet([
        {'years': [2007, 2009, 2008], 'name': 'Seek You Too', 'url': 'http://cq2.nl'},
        {'years': [2009, 2011], 'name': 'Seecr', 'url': 'http://seecr.nl', 'text': 'some optional text' + 10 * " and some more"},
    ])
    assert copyrightSet1 == copyrightSet2

def test_not_equals():
    copyrightSet1 = CopyrightSet([
        {'years': [2011, 2010], 'name': 'Seecr', 'url': 'http://seecr.nl', 'text': 'some optional text' + 10 * " and some more"},
        {'years': [2007, 2009, 2008], 'name': 'Seek You Too', 'url': 'http://cq2.nl'},
    ])

    copyrightSet2 = CopyrightSet([
        {'years': [2007, 2009, 2008], 'name': 'Seek You Too', 'url': 'http://cq2.nl'},
        {'years': [2009, 2011], 'name': 'Seecr', 'url': 'http://seecr.nl', 'text': 'some optional text' + 10 * " and some more"},
    ])
    assert copyrightSet1 != copyrightSet2

def test_more_input_lines_per_copyright_holder():
    copyrightSet = CopyrightSet([
        {'years': [2008], 'name': 'Seek You Too', 'url': 'http://cq2.com'},
        {'years': [2009], 'name': 'Seek You Too', 'url': 'http://seekyoutoo.nl'},
    ])

    assert copyrightSet.asCopyrightLines() == "\
Copyright (C) 2008-2009 Seek You Too http://seekyoutoo.nl\n\
"


def test_serialize_years():
    assert _serializeYears([2007]) == "2007"
    assert _serializeYears([2007, 2009, 2010, 2011]) == "2007, 2009-2011"
    assert _serializeYears([2007, 2009, 2010, 2011, 2013]) == "2007, 2009-2011, 2013"

def test_merge():
    copyrightSet1 = CopyrightSet([
        {'years': [2006], 'name': 'Past Inc.', 'url': 'http://past.url'},
        {'years': [2007], 'name': 'Now Inc.', 'url': 'http://now.url', 'text': 'watch this space'},
        {'years': [2009, 2011], 'name': 'Seecr', 'url': 'http://seecr.nl', 'text': 'some optional text'},
        {'years': [2007, 2009, 2008], 'name': 'Seek You Too', 'url': 'http://cq2.com'},
    ])

    copyrightSet2 = CopyrightSet([
        {'years': [2007], 'name': 'Now Inc.', 'url': 'http://now.url'},
        {'years': [2010], 'name': 'Seecr', 'url': 'http://seecr.nl', 'text': 'some optional text'},
        {'years': [2010], 'name': 'Seek You Too', 'url': 'http://seekyoutoo.nl', 'text': 'will be renamed in 2011'},
        {'years': [2015], 'name': 'Future Inc.', 'url': 'http://future.url'},
    ])

    copyrightSetMerged = copyrightSet1.merge(copyrightSet2)

    assert copyrightSetMerged.asCopyrightLines() == "\
Copyright (C) 2006 Past Inc. http://past.url\n\
Copyright (C) 2007 Now Inc. http://now.url\n\
Copyright (C) 2007-2010 Seek You Too http://seekyoutoo.nl\n\
    will be renamed in 2011\n\
Copyright (C) 2009-2011 Seecr http://seecr.nl\n\
    some optional text\n\
Copyright (C) 2015 Future Inc. http://future.url\n\
"


