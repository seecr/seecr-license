from .applylicense import ApplyLicense, licenses
from .sourcefile import markersByExtension, markersByFilename

explain = """
This applies a license to one or more files or directories.

The given license will be applied to following files:
    %(supportedTypes)s

Licenses available:
    %(supportedLicenses)s

If a license is present it will be replaced with the copyright lines merged
with what is specified in the config file.

If not present, the license is inserted at the first line,
unless first line starts with #!..., then at line 2
unless second line contains # -*- coding ...

The config file must be valid JSON.
Example:
{
    "project": "Some Project",
    "description": "This is just a\\ndummy project\\nfor testing purposes,\\nwith 'all rights reserved' license.",
    "license": "arr",
    "copyrights": {
        "seecr": {"name": "Seecr (Seek You Too B.V.)", "url": "http://seecr.nl"},
        "cq2": {"name": "Seek You Too B.V. (CQ2)", "url": "http://www.cq2.nl",
             "text": "Some optional text"}
    }
}""" % dict(
       supportedTypes='; '.join(['*' + ext for ext in list(markersByExtension.keys())] + list(markersByFilename.keys())),
       supportedLicenses='; '.join(list(licenses.keys()))
    )

def main(args=None):
    from argparse import ArgumentParser, RawDescriptionHelpFormatter
    parser = ArgumentParser(epilog=explain, formatter_class=RawDescriptionHelpFormatter)
    parser.add_argument('configPath', metavar='<configFile>', help='path to config file.')
    parser.add_argument('path', metavar='<file|directory>', help='file or directory to which license needs to be applied.', nargs='+')
    parser.add_argument('--force', action="store_true", default=False, dest='forceUpdate', help="""Use this to force the license onto the files. This can be handy when files have been moved from other projects but their copyright holders have already been updated. By forcing the license onto the file they project name and description in the license will be updated.""")
    parser.add_argument('--changed-only', action="store_true", default=False, dest="changedOnly", help="Only changed files")
    parser.add_argument('--dry-run', action="store_true", default=False, dest="dryRun", help="Show what would be changed")
    parser.add_argument('-y', '--year', default=None, dest="year", help="Use given year in license or current year if not set")
    parser.add_argument('--select', help='Select which copyright holders should be applied. Comma separated. ie: "seecr,cq2"')

    args = parser.parse_args(args)

    try:
        applyLicense = ApplyLicense.fromFile(**vars(args))
        applyLicense.run(args.path)
    except IOError as e:
        print(e)
        parser.print_help()


