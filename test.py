import datetime
from app.core.config import settings

start = datetime.date.fromisoformat(settings.start_date)
end = datetime.date.fromisoformat(settings.end_date)

duration = (end - start) + datetime.timedelta(days=1)

days = []

for i in range(duration.days):
    day = start + datetime.timedelta(days=i)
    days.append(day.strftime("%m-%d"))

print(days)