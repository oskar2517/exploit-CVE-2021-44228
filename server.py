import http.server
import socketserver
import multiprocessing

DIRECTORY = "./server/"

def exploit_server(port, directory=DIRECTORY):
    class Handler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=directory, **kwargs)

        # Disable logs
        def log_message(self, format, *args) -> None:
            return None

    with socketserver.TCPServer(("", port), Handler) as httpd:
        httpd.serve_forever()

if __name__ == "__main__":
    server = multiprocessing.Process(target=exploit_server, args=('8888', ))
    server.start()
    print("Running")