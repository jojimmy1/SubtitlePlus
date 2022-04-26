# import time
# a = time.strftime('%H:%M:%S', time.gmtime(67000))
# print(type(a))
# print(a)

# b = 65.0121 % 1
# print(b)

# import sched, time, datetime
# a = time.strptime('May 01 23:05:17 2018', '%b %d %H:%M:%S %Y')
# print(a)

# def action1():
#     print(datetime.now())

# # Set up scheduler
# s = sched.scheduler(time.localtime, time.sleep)
# # Schedule when you want the action to occur
# s.enterabs(time.strptime('Apr 25 01:16:17 2022', '%b %d %H:%M:%S %Y'), 0, action1)
# # Block until the action has been run
# s.run()

# print("here you go")

import os.path
print(os.path.exists("./draft1.txt"))