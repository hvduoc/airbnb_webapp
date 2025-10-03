from db import get_session
from models import Salesperson

with get_session() as session:
    session.add(Salesperson(name="Nguyễn Văn A", commission_rate=0.05))
    session.add(Salesperson(name="Trần Thị B", commission_rate=0.04))
    session.commit()
