import datetime

current_utc_time = datetime.datetime.utcnow()
def format_timedelta(time):
    total_seconds = (time - datetime.datetime.utcnow()).total_seconds()

    years, remainder = divmod(total_seconds, 365 * 24 * 3600)
    months, remainder = divmod(remainder, 30.4 * 24 * 3600)
    weeks, remainder = divmod(remainder, 7 * 24 * 3600)
    days, remainder = divmod(remainder, 24 * 3600)
    hours, remainder = divmod(remainder, 3600)
    minutes, seconds = divmod(remainder, 60)
    

    

    return {'years':int(years), 'months':int(months), 'weeks':int(weeks), 'days':int(days), 'hours':int(hours), 'minutes':int(minutes), 'seconds':int(seconds)}


result = format_timedelta(datetime.datetime.now())

print(result['seconds'])