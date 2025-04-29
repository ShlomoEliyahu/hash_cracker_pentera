import subprocess
import json
import os
import logging

logging.basicConfig(filename="run_minions.log", format='%(levelname)s %(asctime)s %(message)s', filemode='w')
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def start_minions(minions):
    processes = []

    for host in minions:
        p = subprocess.Popen(["python", "minion.py", str(host['ip']), str(host['port'])])
        processes.append(p)
        if p.poll() is not None:
            logger.error(f"Minion {str(host['ip'])}:{str(host['port'])} exited early with return code {p.returncode}")
        else:
            logger.info(f"Minion {str(host['ip'])}:{str(host['port'])} is running")

    logger.info(f"{len(minions)} minions are now running.")

    try:
        for p in processes:
            p.wait()
    except KeyboardInterrupt:
        logger.info("Stopping all minions...")
        for p in processes:
            p.terminate()

def main():
    minion_config_path = os.environ.get('config_path')
    if not minion_config_path:
        logger.error("Please set the 'config_path' environment variable.")
        exit(1)

    with open(minion_config_path) as f:
        minions = json.load(f)['hosts']

    start_minions(minions)

if __name__ == '__main__':
    main()
