import time, os, sys

num_iterations = 10
cur_iteration = 0

while cur_iteration < num_iterations:
    os.system("netrics --plugin vca")
    time.sleep(45)
    cur_iteration += 1

