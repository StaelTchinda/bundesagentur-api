import argparse


def parse_args():
    parser = argparse.ArgumentParser("Search applicants in the local DB and fetch details from Arbeitsagentur API")


    return parser.parse_args()


def main():
    args = parse_args()
    print(f"Not implemented yet")


if __name__ == "__main__":
    main()