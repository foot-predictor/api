from fastapi import APIRouter

from .competitions import router as router_competitions
from .simulations import router as router_simulations
from .teams import router as router_teams

__version__ = 1

router = APIRouter()


router.include_router(router_teams, prefix="/teams", tags=["Teams"])
router.include_router(
    router_competitions, prefix="/competitions", tags=["Competitions"]
)
router.include_router(router_simulations, prefix="/simulations", tags=["Simulations"])
