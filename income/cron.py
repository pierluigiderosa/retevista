from django_cron import CronJobBase, Schedule
from datetime import datetime
from get_data_stations import get_and_put
from aggregate_data import aggrega

class MyCronJob(CronJobBase):
    RUN_EVERY_MINS = 2 # every 2 hours

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'my_app.my_cron_job'    # a unique code

    def do(self):
        with open("/tmp/test.txt", "a") as myfile:
            myfile.write(str(datetime.now())+'----\n')
        print str(datetime.now())
        pass    # do your thing here


class get_data(CronJobBase):
    RUN_EVERY_MINS = 2
    RUN_AT_TIMES = ['00:15',
                    '01:15',
                    '02:15',
                    '03:15',
                    '04:15',
                    '05:15',
                    '06:15',
                    '07:15',
                    '08:15',
                    '09:15',
                    '10:15',
                    '11:15',
                    '12:15',
                    '13:15',
                    '14:15',
                    '15:15',
                    '16:15',
                    '17:15',
                    '18:15',
                    '19:15',
                    '20:15',
                    '21:15',
                    '22:15',
                    '23:15'
                    ]

    schedule = Schedule(run_at_times=RUN_AT_TIMES)
    code = 'income.get_data'    # a unique code

    def do(self):
        print 'fatto get_data() alle'
        print str(datetime.now())
        get_and_put()


class aggregate_data(CronJobBase):
    RUN_AT_TIMES = ['02:00']

    schedule = Schedule(run_at_times=RUN_AT_TIMES)
    code = 'income.aggregate_data'  # a unique code

    def do(self):
        print 'fatto aggrega() alle'
        print str(datetime.now())
        aggrega()
