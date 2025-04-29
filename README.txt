Distributed MD5 Phone Number Cracker
This project is a distributed password (MD5 hash) cracking system that simulates real-world parallelized password cracking using a master-worker architecture.
It uses a master server to distribute work across multiple minion servers, each trying to crack an MD5 hash representing an Israeli phone number (format: 05X-XXXXXXX).


How It Works
Passwords are phone numbers from a given range (0500000000 to 0599999999).
Hashes are stored in a text file (hashes.txt) with one hash per line.
The master server reads the hashes and divides the number range between multiple minions.
Each minion receives a portion of the number range and attempts to find the password matching the hash by generating MD5 hashes.
Results are logged and displayed once found.


Project Structure
├── master.py           # Master server that manages hash distribution and minions
├── minion.py           # Minion Flask server that cracks a hash in a range
├── run_minions.py      # Script to launch all minions defined in the config
├── config.json         # Configuration file
├── hashes.txt          # Input file with MD5 hashes to crack
├── master.log          # Log file for master actions and results
└── minion_<ip>_<port>.log  # Individual log files per minion


Requirements
Python 3.8+

Configuration
Edit the config.json file to define the range of phone numbers and the IP/port of each minion:
{
  "hosts": [
    {"ip": "127.0.0.1", "port": 5001},
    {"ip": "127.0.0.1", "port": 5002},
    {"ip": "127.0.0.1", "port": 5003}
  ],
  "timeout": 180,
  "retries": 3,
  "range_start": 500000000,
  "range_end": 600000000
}


How to Run
1. Set the environment variable for the config path
2. Start the minion servers - python run_minions.py
3. Run the master
4. Create a file with one MD5 hash per line. You will be prompted to provide its path when running the master.



Crash Handling
The system will retry failed minion requests up to the number of retries defined in config.json.
If a minion doesn't respond within the timeout window, the master logs the failure and continues.
Logging is available in master.log and individual minion_<ip>_<port>.log files.

