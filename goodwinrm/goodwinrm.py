import argparse
from base64 import b64encode
from prompt_toolkit import print_formatted_text as printf, HTML, ANSI, PromptSession
from prompt_toolkit.completion import WordCompleter
from winrm.protocol import Protocol

# Print the banner
def PrintBanner():
    banner = HTML("""
> <ansigreen>┏┓     ┓┓ ┏•  ┳┓ ┳┳┓</ansigreen>  <b>GoodWinRM - v0.1</b>
> <ansigreen>┃┓┏┓┏┓┏┫┃┃┃┓┏┓┣┻┓┃┃┃</ansigreen>  Python WinRM Remote Shell
> <ansigreen>┗┛┗┛┗┛┗┻┗┻┛┗┛┗┛ ┗┛ ┗</ansigreen>  <ansiblue>https://github.com/h3x0c4t/goodwinrm</ansiblue>
    """)

    printf(banner)

# Parse the command line arguments
def ParseArguments():
    parser = argparse.ArgumentParser(description="WinRM Remote Shell")
    parser.add_argument("-i", "--ip", help="Remote host IP or hostname.", required=True)
    parser.add_argument("-u", "--username", help="Username.", required=True)
    parser.add_argument("-p", "--password", help="Password.", required=True)
    parser.add_argument("-t", "--transport", help="Transport protocol. ['basic', 'ntlm', 'kerberos', 'credssp', 'ssl', 'certificate']", default="basic")
    parser.add_argument("-v", "--server_cert_validation", help="Server certificate validation. ['ignore', 'validate']", default="ignore")
    parser.add_argument("-d", "--directory", help="Working directory.", default="C:\\")
    parser.add_argument("--https", help="Use HTTPS.", type=bool, default=False)
    args = parser.parse_args()
    return args

def PrintError(message):
    printf(ANSI("\x1b[31m[!] {0}\x1b[0m").format(message))

def PrintSuccess(message):
    printf(ANSI("\x1b[32m[+] {0}\x1b[0m").format(message))

# Open a remote shell
# server_cert_validation values: "ignore", "validate"
# transport values: "basic", "ntlm", "kerberos", "credssp", "ssl", "certificate"
def OpenRemoteShell(address, username, password, https=False, transport="basic", server_cert_validation="ignore", directory="C:\\"):
    address = address.strip().split(":")
    if len(address) == 2:
        address, port = address
    else:
        address = address[0]
        port = 0

    if https:
        if port == 0:
            port = 5986
        endpoint = f"https://{address}:{port}/wsman"
    else:
        if port == 0:
            port = 5985
        endpoint = f"http://{address}:{port}/wsman"

    p = Protocol(
        endpoint=endpoint,
        transport=transport,
        username=username,
        password=password,
        server_cert_validation=server_cert_validation
    )
    try:
        shell_id = p.open_shell(codepage=65001, working_directory=directory)
        PrintSuccess(f"Successfully connected to {address}.")
        print()
    except Exception as e:
        PrintError(f"Fatal: {e}")
        exit(1)
    return p, shell_id
    
def ExecuteCommand(cmd, p, shell_id):
    encyptedCmd = b64encode(cmd.encode("utf_16_le")).decode("ascii")
    command_id = p.run_command(shell_id, f"powershell -enc {encyptedCmd}")
    std_out, std_err, status_code = p.get_command_output(shell_id, command_id)
    p.cleanup_command(shell_id, command_id)

    if status_code != 0:
        if std_out:
            PrintError(std_out.decode("utf-8", "replace").strip())
        if std_err:
            PrintError(f"Error: {std_err.decode('utf-8', 'replace').strip()}")
        return

    output = std_out.decode("utf-8", "replace")
    print(output.strip())

def main():
    PrintBanner()
    
    args = ParseArguments()
    p, shell_id = OpenRemoteShell(
        args.ip, 
        args.username, 
        args.password, 
        https=args.https,
        transport=args.transport, 
        server_cert_validation=args.server_cert_validation, 
        directory=args.directory
    )

    session = PromptSession()
    completer = WordCompleter(["exit", "clear"])
    while(True):
        cmd = session.prompt(ANSI(f"\x1b[34m{args.username}@{args.ip}\x1b[0m > "), completer=completer)
        if cmd == "exit":
            break
        if cmd == "clear":
            # Only works in Linux
            print("\033[H\033[J")
            continue
        if cmd == "":
            continue

        ExecuteCommand(cmd, p, shell_id)
        

    p.close_shell(shell_id)

if __name__ == "__main__":
    main()