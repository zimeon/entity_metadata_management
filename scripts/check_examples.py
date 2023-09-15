"""Check validity of JSON examples in EMM specification.

Intended to be used with Github CI so has a zero exit code
on success, non-zero otherwise.
"""
import argparse
import json
import marko
import os.path
import re
import sys


def check_example(section, example_json):
    """Check example, return 1 for fail, 0 for OK."""
    if re.match(r'''\s*"''', example_json):
        example_json = '{' + example_json + '}'
    # Remove any comments (not legal in JSON), assume
    # in an object so replace with property pair to make
    # comma on previous line OK
    example_json = re.sub(r'''^\s*//.*$''', '  "comment": "removed"', example_json, flags=re.MULTILINE)
    try:
        example = json.loads(example_json)
    except Exception as e:  # wildly different exceptions in python 2 & 3
        print("Example in section '%s' -- JSON PARSING FAILED" % (section))
        if args.verbose or args.very_verbose:
            print(str(e))
        if args.very_verbose:
            print(example_json)
        return 1
    print("Example in section '%s' -- OK" % (section))
    return 0


parser = argparse.ArgumentParser(description="Check JSON in EMM specification examples. Zero exit on success.",
                                 formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument("-d", "--spec-dir", default="docs/0.1",
                    help="Specification direct")
parser.add_argument("-v", "--verbose", action='store_true',
                    help="Be verbose, show error details")
parser.add_argument("-V", "--very-verbose", action='store_true',
                    help="Be very verbose, show JSON for failures")
args = parser.parse_args()

md_file = os.path.join(args.spec_dir, 'index.md')
if not os.path.exists(md_file):
    print("No spec file " + md_file + ", nothing to do!")
    sys.exit(0)

with open(md_file, 'r') as fh:
    spec_md = fh.read()

errors = 0
spec = marko.parse(spec_md)
section = "unknown"
for element in spec.children:
    if type(element) == marko.block.Heading:
        section = element.children[0].children
    # FIXME: Structure of code block inside blockquotes doesn't
    # FIXME: seem the same as top level examples. Currently not
    # FIXME: validating json snippets in blockquotes
    # elif type(element) == marko.block.Quote:
    #    for sub_el in element.children:
    #        print(sub_el)
    #        if type(sub_el) == marko.block.FencedCode and element.lang == 'json':
    #            errors += check_example(section, rawtext.sub_el.children[0]children)
    elif type(element) == marko.block.FencedCode and \
             (element.lang in ('json', 'json-doc')):
        errors += check_example(section, element.children[0].children)

sys.exit(errors)
