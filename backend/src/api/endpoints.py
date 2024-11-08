import fastapi

from src.api.routes.category import router as category_router
from src.api.routes.expense import router as expense_router
from src.api.routes.user import router as user_router

router = fastapi.APIRouter()
router.include_router(router=user_router)
router.include_router(router=category_router)
router.include_router(router=expense_router)
