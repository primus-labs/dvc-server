import http.server
import ssl
import json
import subprocess
import json
import os
from multiprocessing import Process, Value, Manager
import time
from dotenv import load_dotenv

load_dotenv(override=True)

is_busy = Value("i", 0)  # 0: idle, 1: busy
manager = Manager()
tasks = manager.dict()
start = time.perf_counter()


def run_command_succinct(version, requestid, attestationData):
    t_start = time.perf_counter()
    try:
        input_dir = f"./request_data"
        output_dir = f"./proof_output/{requestid}"
        os.makedirs(input_dir, exist_ok=True)
        os.makedirs(output_dir, exist_ok=True)

        input_file = f"{input_dir}/{requestid}.json"
        with open(input_file, "w", encoding="utf-8") as f:
            f.write(attestationData)

        cmd = [
            "./bin/zktls",
            "--prove",
            "--input",
            input_file,
            "--output-dir",
            output_dir,
        ]
        if version is not None:
            cmd[0] = f"./bin/zktls.{version}"
        print("[CMD]", cmd)
        result = subprocess.run(cmd, capture_output=True, text=True)
        # result = subprocess.run(cmd, capture_output=True, text=True, env=env)
        print("[OUTPUT]:", result.stdout)
        if result.stderr:
            print("[ERROR]:", result.stderr)

        proof_fixture = ""
        if os.path.exists(f"{output_dir}/proof_fixture.json"):
            with open(f"{output_dir}/proof_fixture.json", "r", encoding="utf-8") as f:
                proof_fixture = f.read()

        t_end = time.perf_counter()
        tasks[requestid] = {
            "status": "done",
            "returncode": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "proof_fixture": proof_fixture,
            "elapsed": f"{t_end - t_start:.6f}",
        }
        print(f"[ELAPSED]: {t_end - t_start:.6f}")
    except Exception as e:
        print("[EXCEPTION]:", str(e))
        t_end = time.perf_counter()
        tasks[requestid] = {
            "status": "error",
            "returncode": -1,
            "stdout": "",
            "stderr": str(e),
            "proof_fixture": "",
            "elapsed": f"{t_end - t_start:.6f}",
        }
        print(f"[ELAPSED]: {t_end - t_start:.6f}")
    finally:
        is_busy.value = 0


class SimpleHTTPSRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET,POST,OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "*")
        # self.send_header("Access-Control-Allow-Credentials", "true")  # If credentials (cookies) are needed
        self.send_header("Referrer-Policy", "strict-origin-when-cross-origin")
        super().end_headers()

    def end_200(self, data):
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode("utf-8"))

    def do_OPTIONS(self):  # Handle preflight requests
        self.send_response(200, "OK")
        self.end_headers()

    def do_POST(self):
        if self.path not in ["/zktls/prove", "/zktls/result"]:
            data = {"code": "10001", "description": "only support /zktls/prove, /zktls/result"}
            self.end_200(data)
            return

        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length).decode("utf-8")
        print("body", body)

        data = json.loads(body)
        data.setdefault("version", None)
        requestid = data["requestid"]
        version = data["version"]

        if self.path == "/zktls/is_busy":
            if is_busy.value == 1:
                data = {"code": "10002", "description": "Server is busy, please try later."}
                self.end_200(data)
            else:
                data = {"code": "0", "description": "free."}
                self.end_200(data)
        elif self.path == "/zktls/prove":
            if is_busy.value == 1:
                data = {"code": "10002", "description": "Server is busy, please try later."}
                self.end_200(data)
                return

            # the body is json string
            attestationData = json.dumps(data["attestationData"], separators=(",", ":"), ensure_ascii=False)
            print("requestid", requestid)
            print("attestationData", attestationData)

            # set status
            is_busy.value = 1
            tasks[requestid] = {"status": "running"}

            # execute prove program
            Process(target=run_command_succinct, args=(version, requestid, attestationData)).start()

            # response
            data = {"code": "0", "description": "success"}
            self.end_200(data)
        elif self.path == "/zktls/result":
            task = tasks.get(requestid)
            if not task:
                data = {"code": "10003", "description": f"requestid {requestid} not exist!"}
                self.end_200(data)
                return

            data = {
                "code": "0",
                "description": "success",
                "details": task,
            }
            self.end_200(data)


port = int(os.getenv("PORT", 8080))
use_ssl = os.getenv("USE_SSL", "OFF").upper() == "ON"
certfile = os.getenv("CERTFILE")
keyfile = os.getenv("KEYFILE")
if use_ssl:
    if not certfile or not keyfile:
        raise ValueError("SSL enabled but CERTFILE or KEYFILE not provided.")

httpd = http.server.HTTPServer(("0.0.0.0", port), SimpleHTTPSRequestHandler)

if use_ssl:
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain(certfile=certfile, keyfile=keyfile)
    httpd.socket = context.wrap_socket(httpd.socket, server_side=True)

print(f'Serving HTTP{"S" if use_ssl else ""} on 0.0.0.0:{port}')
httpd.serve_forever()
