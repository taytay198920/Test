# -*- coding: UTF-8 -*-
# @Time     : 2026/4/4
# @Author   : Li
# @File     : cli.py


import subprocess
from libs.handle_log import log


def execute(command):
    log.info("Executing command: %s", command)
    try:
        p = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=30, text=True)
    except subprocess.TimeoutExpired:
        log.info("Command timed out")
        return {"error": "Command timed out"}
    else:
        returncode = p.returncode
        stdout = p.stdout
        stderr = p.stderr
        response = {"success": True, "stdout": stdout, "stderr": stderr, "returncode": returncode}
        log.debug("command response: %s", response)
        return response