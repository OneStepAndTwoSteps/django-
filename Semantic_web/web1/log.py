#author py chen
import logging
import logging.handlers
import datetime
from django.dispatch import receiver
from django.db.models.signals import post_save
# from web1.models import Account

@receiver(post_save)
def write_log(sender,**kwargs):
    '''创建一个Logger对象
    logging.getLogger()方法有一个可选参数name，该参数表示将要返回的日志器的名称标识，如果不提供该参数，则其值为'root'。
    若以相同的name参数值多次调用getLogger()方法，将会返回指向同一个logger对象的引用。
    '''
    print("開始執行write_log")
    logger = logging.getLogger('mylogger')
    logger.setLevel(logging.DEBUG)

    rf_handler = logging.handlers.TimedRotatingFileHandler('log_file.txt', when='midnight', interval=1, backupCount=7, atTime=datetime.time(0, 0, 0, 0))
    rf_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))


    logger.addHandler(rf_handler)

    print(sender,kwargs)
    # print(sender,kwargs["info"])
    print("signal",kwargs['signal'])
    print("signal",kwargs)
    '''触发不同级别的日志 严重度从小到大debug，info，warning，error，critical'''
    logger.debug(kwargs)

# post_save.connect(write_log)
