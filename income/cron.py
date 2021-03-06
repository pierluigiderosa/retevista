from django_cron import CronJobBase, Schedule
from datetime import datetime
from income.get_data_stations import get_and_put
from income.aggregate_data import aggrega
from dash_aziende.forecast import save_forecast
from consiglio.bilancio_idrico import calc_bilancio_campo

class MyCronJob(CronJobBase):
    RUN_EVERY_MINS = 1 # every 2 hours

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'my_app.my_cron_job'    # a unique code

    def do(self):
        with open("/tmp/test.txt", "a") as myfile:
            myfile.write(str(datetime.now())+'----\n')
        print str(datetime.now())
        print 'sono qua'
        pass    # do your thing here
        print 'sono qua 2'

class get_data(CronJobBase):
    # RUN_EVERY_MINS = 2
    RETRY_AFTER_FAILURE_MINS = 5
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

    schedule = Schedule(run_at_times=RUN_AT_TIMES,retry_after_failure_mins=RETRY_AFTER_FAILURE_MINS)
    code = 'income.get_data'    # a unique code

    def do(self):
        print 'fatto get_data() alle'
        print str(datetime.now())
        get_and_put()


class aggregate_data(CronJobBase):
    RUN_AT_TIMES = ['01:15']
    RETRY_AFTER_FAILURE_MINS = 5

    schedule = Schedule(run_at_times=RUN_AT_TIMES,retry_after_failure_mins=RETRY_AFTER_FAILURE_MINS)
    code = 'income.aggregate_data'  # a unique code

    def do(self):
        print 'fatto aggrega() alle'
        print str(datetime.now())
        aggrega()


class do_bilancio(CronJobBase):
    RUN_AT_TIMES = ['02:00']
    RETRY_AFTER_FAILURE_MINS = 15

    schedule = Schedule(run_at_times=RUN_AT_TIMES,retry_after_failure_mins=RETRY_AFTER_FAILURE_MINS)
    code = 'consiglio.bilancio'  # a unique code

    def do(self):
        print 'calcolo bilancio alle'
        print str(datetime.now())
        # calc_bilancio()
        calc_bilancio_campo()

class get_forecast(CronJobBase):
    RUN_AT_TIMES = ['03:00']
    RETRY_AFTER_FAILURE_MINS = 5

    schedule = Schedule(run_at_times=RUN_AT_TIMES, retry_after_failure_mins=RETRY_AFTER_FAILURE_MINS)
    code = 'dash.forecast'  # a unique code

    def do(self):
        print 'prese previsioni'
        print str(datetime.now())
        save_forecast()

# class do_bilancioCampi(CronJobBase):
#     RUN_AT_TIMES = ['01:10']
#     RETRY_AFTER_FAILURE_MINS = 5
#
#     schedule = Schedule(run_at_times=RUN_AT_TIMES,retry_after_failure_mins=RETRY_AFTER_FAILURE_MINS)
#     code = 'consiglio.bilancio.appezzamentoCampo'  # a unique code
#
#     def do(self):
#         print 'calcolo bilancio per i campi alle'
#         print str(datetime.now())
#         calc_bilancio_campo()