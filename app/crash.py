from datetime import datetime
from .const import *
import os

def handle_crash_report(code: int, message: str):
    '''
    处理崩溃报告，将崩溃信息保存到文件中。
    Arguments:
        code (int): 崩溃代码，表示崩溃的类型或原因。
        message (str): 崩溃消息，提供关于崩溃的详细信息。

    Returns:
        None
    '''

    print(f'''Application Crashed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}. Caused by: ({code}) {message}''')

    with open(os.path.join(CRASH_REPORT_PATH, f'{datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.txt'), 'w') as f:
        f.write(f'''Crash Report - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n({code}){message}''')


