import pandas as pd
from ..dependencies import get_current_user
from ..helper_functions import changeCandleTimeFrame
from ..models.models import MinuteBars
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm.session import Session

from ..db_conf import db_session

db: Session = db_session.session_factory()
router = APIRouter(
    prefix='/kline',
    tags=['kline'],
    # dependencies=[Depends(get_current_user)],
    responses={404: {"description": "Not Found"}}
)


@router.get("/minuteBars/")
def get_minutes(symbol_id: int, timeframe: str):

    minutes = db.query(
        MinuteBars).filter(MinuteBars.symbol_id == symbol_id).all()

    df = pd.DataFrame([m.__dict__ for m in minutes])
    df.drop(['_sa_instance_state', 'symbol_id', 'id'],
            axis=1, inplace=True)
    kline = changeCandleTimeFrame(df, timeframe)

    return kline
