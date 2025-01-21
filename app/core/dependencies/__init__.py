from typing import Annotated

from fastapi import Depends, FastAPI
from sqlmodel import Session

from core.dependencies.base import get_current_app, get_db
from core.dependencies.matches_data_extraction import MatchesDataExtractor

SessionDep = Annotated[Session, Depends(get_db)]
CurrentAppDep = Annotated[FastAPI, Depends(get_current_app)]
MatchExtractorDep = Annotated[MatchesDataExtractor, Depends(MatchesDataExtractor)]
