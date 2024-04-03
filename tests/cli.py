import argparse

from .merge_test import TestAutomater
from meshiphi.utils import setup_logging, timed_call

@setup_logging
def get_args(default_output=None):
    ap = argparse.ArgumentParser()
    # Add one or two arguments as branches
    # If one, compare current branch to specified one
    # If two, compare one to the other
    ap.add_argument('branch_a', action='append')
    ap.add_argument('branch_b', nargs='?', action='append')

    # Want only regression tests
    ap.add_argument("-r", "--regression",
                    default=False,
                    action="store_true",
                    help="Run only regression tests")
    # Want only unit tests
    ap.add_argument("-u", "--unit",
                    default=False,
                    action="store_true",
                    help="Run only unit tests")
    # Output file specified
    ap.add_argument("-o", "--output",
                    default=default_output,
                    help="Output file")
    # Verbose logging specified
    ap.add_argument("-v", "--verbose",
                    default=False,
                    action="store_true",
                    help="Turn on DEBUG level logging")
    
    return ap.parse_args()
    
@timed_call
def merge_test_cli():

    default_output = "pytest.meshiphi.log"
    args = get_args(default_output=default_output)

    # Default is both are true. Turn one off if only one specified
    if args.regression and not args.unit:
        reg  = True
        unit = False
    elif args.unit and not args.regressions:
        unit = True
        reg  = False
    else:
        reg  = True
        unit = True

    # Set appropriate from/into branch to pass to TestAutomater
    if args.branch_b != [None]:
        from_branch = args.branch_a[0]
        into_branch = args.branch_b[0]
    else:
        from_branch = None
        into_branch = args.branch_a[0]

    # Select and run appropriate tests
    TestAutomater(from_branch=from_branch, 
                  into_branch=into_branch,
                  regression=reg,
                  unit=unit)