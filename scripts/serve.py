#!/usr/bin/env python3
"""로컬 미리보기 서버. 캐시를 끄고 서빙하므로 새로고침만으로 항상 최신 파일이 보입니다.

    python3 scripts/serve.py          # http://127.0.0.1:8765
    python3 scripts/serve.py 9000     # 포트 지정
"""
import functools, http.server, os, socketserver, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8765


class NoCacheHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Cache-Control", "no-store, no-cache, must-revalidate, max-age=0")
        self.send_header("Pragma", "no-cache")
        self.send_header("Expires", "0")
        super().end_headers()

    def log_message(self, fmt, *args):
        pass


socketserver.TCPServer.allow_reuse_address = True
handler = functools.partial(NoCacheHandler, directory=ROOT)
with socketserver.TCPServer(("127.0.0.1", PORT), handler) as httpd:
    print("http://127.0.0.1:%d  (캐시 없음, Ctrl+C 로 종료)" % PORT)
    httpd.serve_forever()
