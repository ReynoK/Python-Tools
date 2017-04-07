import re

class Crontab(object):

    every_dash = re.compile(r'\*/(\d+)')            # */n
    range_dash = re.compile(r'(\d+)-(\d+)/(\d+)')   #i-j/n
    range_ = re.compile(r'(\d+)-(\d+)')             #i-j 优先级依次降低

    def __init__(self, minute='*', hour='*', day='*', week='*', month='*'):

        self._minute = minute
        self._hour = hour
        self._day = day
        self._week = week
        self._month = month
        self._crontab_setting = dict()
        self._generate_rule()


    def _generate_rule(self):

        validation = {
            ('m', self._minute, range(0,60)),   #分钟
            ('h', self._hour, range(0,25)),     #小时
            ('d', self._day, range(1,32)),      #日期
            ('w', self._week, range(0,7)),      #星期(0-6) 0表示星期天
            ('M', self._month, range(1,13)),    #月份
        }

        for (label, value, legal) in validation:
            collect = set()

            if isinstance(value, int):
                value = str(value)

            for part in value.split(','):       # 逗号的优先级最高

                if part.isdigit():              # 纯数字
                    part = int(part)
                    if part not in legal:
                        raise ValueError('label({0}) illegal'.format(value))
                    collect.add(part)
                    continue

                if part == '*':                 # 全部
                    collect.update(legal)
                    continue

                every_dash_match = self.every_dash.match(part)
                if every_dash_match:                    # */n
                    interval, = map(int, every_dash_match.groups())
                    collect.update(legal[::interval])
                    continue

                range_dash_match = self.range_dash.match(part)
                if range_dash_match:                    # i-j/n
                    start,end,interval = map(int, range_dash_match.groups())
                    if start not in legal or end not in legal:
                        raise ValueError('label({0}) illegal'.format(value))
                    collect.update(range(start, end + 1, interval))
                    continue

                range_match = self.range_.match(part)
                if range_match:                         # i-j
                    start,end = map(int, range_match.groups())
                    if start not in legal or end not in legal:
                        raise ValueError('label({0}) illegal'.format(value))
                    collect.update(range(start, end + 1))
                    continue

            self._crontab_setting[label] = sorted(list(collect))

    def validate_datetime(self, date_time):
        _, month, day, hour, minute, _, week, _, _ = date_time.timetuple()

        # 在datetime中,week=0表示星期一,这里要转换
        week = (week + 1) % 7

        for label,value in zip(['M','d','h','m','w'],[month,day,hour,minute,week]):
            if value not in self._crontab_setting[label]:
                return False

        return True

if __name__ == '__main__':

    crontab = Crontab(month='1-12/3')
    import datetime

    print(crontab.validate_datetime(datetime.datetime.strptime('2017-04-03','%Y-%m-%d')))
    print(crontab.validate_datetime(datetime.datetime.strptime('2017-05-02', '%Y-%m-%d')))











