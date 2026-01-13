import multiprocessing

# Gunicorn configuration
bind = "0.0.0.0:5000"
workers = multiprocessing.cpu_count() * 2 + 1
threads = 2
timeout = 120
keepalive = 2
errorlog = '/home/ubuntu/mujersanaia/log.txt'
accesslog = '/home/ubuntu/mujersanaia/log.txt'
loglevel = 'info'
capture_output = True
enable_stdio_inheritance = True
