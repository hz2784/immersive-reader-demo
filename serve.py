#!/usr/bin/env python3
"""Local dev server with HTTP Range support (needed for <audio> seek)."""
import http.server
import os
import re
import socketserver
import sys


class RangeHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def send_head(self):
        path = self.translate_path(self.path)
        if os.path.isdir(path):
            return super().send_head()
        try:
            f = open(path, 'rb')
        except OSError:
            self.send_error(404)
            return None

        fs = os.fstat(f.fileno())
        size = fs.st_size
        ctype = self.guess_type(path)
        rng = self.headers.get('Range')

        if rng:
            m = re.match(r'bytes=(\d*)-(\d*)', rng)
            if m:
                start = int(m.group(1)) if m.group(1) else 0
                end   = int(m.group(2)) if m.group(2) else size - 1
                end   = min(end, size - 1)
                if start > end or start >= size:
                    self.send_error(416)
                    f.close(); return None
                length = end - start + 1
                self.send_response(206)
                self.send_header('Content-Type', ctype)
                self.send_header('Accept-Ranges', 'bytes')
                self.send_header('Content-Range', f'bytes {start}-{end}/{size}')
                self.send_header('Content-Length', str(length))
                self.end_headers()
                f.seek(start)
                remaining = length
                while remaining:
                    chunk = f.read(min(64 * 1024, remaining))
                    if not chunk: break
                    self.wfile.write(chunk)
                    remaining -= len(chunk)
                f.close()
                return None

        # No range header — normal 200 response
        self.send_response(200)
        self.send_header('Content-Type', ctype)
        self.send_header('Accept-Ranges', 'bytes')
        self.send_header('Content-Length', str(size))
        self.end_headers()
        return f


if __name__ == '__main__':
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8765
    with socketserver.TCPServer(('', port), RangeHTTPRequestHandler) as httpd:
        httpd.allow_reuse_address = True
        print(f'Serving with Range support on http://localhost:{port}/')
        httpd.serve_forever()
