from fastapi import APIRouter

from .simulations import router as router_simulations
from .teams import router as router_teams

__version__ = 1

router = APIRouter()


router.include_router(router_teams, prefix="/teams", tags=["Teams"])
router.include_router(router_simulations, prefix="/simulations", tags=["Simulations"])
