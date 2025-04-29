from typing import Optional
from flask import Flask, request, jsonify
import hashlib
import sys
import logging

logging.basicConfig(filename=f"minion_{sys.argv[1]}_{sys.argv[2]}.log", format='%(levelname)s %(asctime)s %(message)s', filemode='w')
logger = logging.getLogger()
logger.setLevel(logging.INFO)

app = Flask(__name__)

def md5_hash(s: str) -> str:
    return hashlib.md5(s.encode()).hexdigest()

def try_crack(hash_to_crack: str, start: int, end: int) -> Optional[str]:
    for num in range(start, end + 1):
        phone = f"0{num:09d}"
        if md5_hash(phone) == hash_to_crack:
            return phone
    return None


@app.route('/crack', methods=['POST'])
def crack():

    data = request.get_json()
    hash_to_crack = data['hash']
    range_start = int(data['range_start'])
    range_end = int(data['range_end'])

    try:
        hash_result = try_crack(hash_to_crack=hash_to_crack, start=range_start, end=range_end)
    except Exception as e:
        logger.error(f"Something went wrong inside try_crack function \n {e}")

    else:
        if hash_result:
            logger.info(f"[FOUND] Hash {hash_to_crack} => {hash_result}")
            return jsonify({"found": True, "phone": hash_result})
        else:
            logger.info(f"[NOT FOUND] Hash {hash_to_crack} in range {range_start}-{range_end}")
            return jsonify({"found": False})


if __name__ == '__main__':
    ip = str(sys.argv[1])
    port = int(sys.argv[2])

    app.run(host=ip, port=port)