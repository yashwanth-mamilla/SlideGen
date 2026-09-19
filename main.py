#!/usr/bin/env python3
"""SlideGen CLI Entrypoint - Backward compatibility wrapper."""

import sys
from slidegen.cli import main

if __name__ == "__main__":
    sys.exit(main())
