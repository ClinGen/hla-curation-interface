"""Provide the ASGI config.

Expose the ASGI callable as a module-level variable named `application`.
"""

from django.core.wsgi import get_wsgi_application
from dotenv import load_dotenv

# Load environment variables from the `.env` file.
load_dotenv()

application = get_wsgi_application()
