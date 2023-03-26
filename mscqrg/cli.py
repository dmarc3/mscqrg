import argparse
from mscqrg.bulk_data import BULK_DATA

def command_line_interface():
    """Command line interface for qrg utility
    """
    # Parse CLI arguments
    parser = argparse.ArgumentParser(
        prog="qrg",
        description="Provide Quick Reference Guide documentation for specified Bulk Data Entry.",
    )
    parser.add_argument('BULK_DATA_ENTRY', type=str)
    parser.add_argument("-pdf", "--open-pdf", action="store_true", default=False, help="open PDF documentation")
    args = parser.parse_args()

    # Process arguments
    data = BULK_DATA(args.BULK_DATA_ENTRY, pdf=args.open_pdf)
    if args.open_pdf:
        data.open_pdf()
    else:
        print(data)
