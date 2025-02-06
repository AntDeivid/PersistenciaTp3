from src.app.core.config import settings
from src.app.core.logger import setup_logging
from src.app.core.startup import create_application
from src.app.routers.router_center import router

logger = setup_logging()

app = create_application(router = router, settings = settings)