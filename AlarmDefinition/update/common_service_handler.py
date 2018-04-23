#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import sys


def get_watch_data():
    _data = sys.stdin.read()
    _data = json.loads(_data)
    return _data


def get_service_name(data):
    service_name = data[0]['Service']['Service']
    return service_name


def main():
    data = get_watch_data()
    service_name = get_service_name(data)
    if 'udaserver' == service_name:
        import esa_state_handler as esa
        esa.main(data)
    if 'OM-Center' == service_name or service_name is None:
        import esa_state_handler as om
        om.main(data)


if __name__ == '__main__':
    try:
        main()
    except Exception, e:
        print e.message
