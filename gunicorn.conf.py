bind = "0.0.0.0:5000"

# What the providers find upstream is kept in memory for five minutes. A single
# process has one copy of it; with several, each would ask upstream again.
workers = 1
worker_class = "gthread"
threads = 8

# A route answers in about 5 seconds at worst, when nothing is in memory yet
timeout = 60

# /tmp is on disk in a container, and the worker writes to it all the time
worker_tmp_dir = "/dev/shm"

accesslog = "-"
