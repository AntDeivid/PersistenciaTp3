from src.app.core.config import settings
from src.app.core.startup import create_application
from src.app.routers.router_center import router

app = create_application(router = router, settings = settings)