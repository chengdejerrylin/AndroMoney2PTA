import argparse
import csv

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Parse AndroMoney CSV export')
    parser.add_argument('input', type=str, help='AndroMoney CSV file')
    parser.add_argument('output', type=str, help='Output CSV file')
    args = parser.parse_args()
    print(args.filename)