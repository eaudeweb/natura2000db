#!/usr/bin/env python


if __name__ == '__main__':
    import sys
    from manage import manager
    print>>sys.stderr, "rio.py is deprecated, use manage.py"
    manager.run()
