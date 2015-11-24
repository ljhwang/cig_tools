import argparse
import json


def create_main_parser():
    argparse.ArgumentParser(
        description="Where you go to get your software license.",
    )


if __name__ == "__main__":
	main(create_main_parser().parse_args())
