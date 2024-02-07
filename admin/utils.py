import datetime

from peewee import fn, SQL

from Config import config
from models import V2StatUser

game_dict = {
    '🎰老虎机': config.TIGER,
    '🎲骰子': config.DICE,
    '🏀篮球': config.BASKETBALL,
    '⚽足球': config.FOOTBALL,
    '🎯飞镖': config.BULLSEYE,
    '🎳保龄球': config.BOWLING,
}
settings_dict = {
    '🏷️标题设置': 'title',
    '🗑️删除时间': 'delete_message',
    '📅签到设置': 'checkin',
    '✨抽奖设置': 'lucky',
    '💬关键词回复': 'keyword_reply',
    '🆕新成员入群': 'new_members',
}

v2board_dict = {
    '⏱添加时长': 'xx',
    '🚮解绑用户': 'xx',
    '🥇本周排行': 'xx',
    '🏆本月排行': 'xx',
}


def convert_bytes(byte_size):
    suffixes = ['B', 'KB', 'MB', 'GB', 'TB']
    index = 0
    while byte_size >= 1024 and index < len(suffixes) - 1:
        byte_size /= 1024.0
        index += 1
    return f"{byte_size:.2f} {suffixes[index]}"


def statMonth():
    emoji_list = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]
    # 获取当前日期
    current_date = datetime.datetime.now()
    # 计算第一天
    first_day = current_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    # 计算上个月的最后一天
    if first_day.month == 12:
        last_day = current_date.replace(year=current_date.year + 1, month=1, day=1, hour=23, minute=59, second=59,
                                        microsecond=999999)
    else:
        last_day = current_date.replace(month=current_date.month + 1, day=1, hour=23, minute=59, second=59,
                                        microsecond=999999)
    last_day = last_day - datetime.timedelta(days=1)

    timestamp_first_day = int(first_day.timestamp())
    timestamp_last_day = int(last_day.timestamp())
    # - datetime.timedelta(days=1)
    results = (V2StatUser
               .select(V2StatUser, fn.SUM((V2StatUser.u + V2StatUser.d) * V2StatUser.server_rate).alias('total_traffic'))
               .where(V2StatUser.record_at.between(timestamp_first_day, timestamp_last_day))
               .group_by(V2StatUser.user_id)
               .order_by(SQL('total_traffic DESC'))
               .limit(10)
               )
    text = f'📊{first_day.date()}至{current_date.date()}流量前10名\n---------------\n'
    for idx, result in enumerate(results):
        text += f'{emoji_list[idx]}  {result.user_id.email} {convert_bytes(int(result.total_traffic))}\n\n'
    return text


def statDay():
    emoji_list = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]
    
    # 获取当前日期和时间
    current_date = datetime.datetime.now()
    
    # 计算本周的第一天和最后一天
    weekday = current_date.weekday()  # 获取今天是星期几（0代表星期一，6代表星期日）
    sunday = current_date - datetime.timedelta(days=weekday)  # 计算本周的星期日
    saturday = sunday + datetime.timedelta(days=6)  # 计算本周的星期六
    
    # 设置时间范围为本周
    sunday_start = datetime.datetime.combine(sunday, datetime.time.min)
    saturday_end = datetime.datetime.combine(saturday, datetime.time.max)
    timestamp_start = int(sunday_start.timestamp())
    timestamp_end = int(saturday_end.timestamp())
    
    # 查询本周内的流量数据
    results = (V2StatUser
               .select(V2StatUser, fn.SUM((V2StatUser.u + V2StatUser.d) * V2StatUser.server_rate).alias('total_traffic'))
               .where(V2StatUser.record_at.between(timestamp_start, timestamp_end))
               .group_by(V2StatUser.user_id)
               .order_by(SQL('total_traffic DESC'))
               .limit(10)
               )
    
    # 格式化输出文本
    text = f'📊本周流量前10名\n---------------\n'
    for idx, result in enumerate(results):
        text += f'{emoji_list[idx]}  {result.user_id.email} {convert_bytes(int(result.total_traffic))}\n\n'
    return text
