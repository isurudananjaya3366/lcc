"""
LankaCommerce Cloud - Settings Module

Environment-based settings loading.
Checks DJANGO_ENV environment variable to determine which settings to use.

Environment values:
    - local (default): Development settings
    - production: Production settings
    - test: Testing settings
"""

import os

env = os.environ.get("DJANGO_ENV", "local")

if env == "production":
    from config.settings.production import *  # noqa: F401, F403
elif env == "test":
    from config.settings.test import *  # noqa: F401, F403
else:
    from config.settings.local import *  # noqa: F401, F403
