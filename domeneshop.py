#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse

from domeneshop.domeneshop import Domeneshop

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--config', help='Path to config file')
    parser.add_argument('-v', '--verbose', help='Verbose', action='store_true')

    args = parser.parse_args()

    object = Domeneshop(verbose=args.verbose)
    object.update_records()


if __name__ == "__main__":
    main()
