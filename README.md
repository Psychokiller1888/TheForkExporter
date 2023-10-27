# TheForkExporter
Export your customer data without subscription to shameless prices

## Howto
- **Turn off your computer sleep mode, or auto logout after time inactivity!!**
- **Set your TheFork account in english**
- Clone this repo
- Install your venv in it
- Install requirements in your venv
- Open a terminal and start a browser with remote debugging by typing: `start chrome.exe --remote-debugging-port=9222`
- In the browser that just opened, navigate to manager.thefork.com
- Log in to your account and stay on that page!
- Start this script and let it work by itself
- Your customer data will be dumped into `data.csv`

## Command options:
- --debug true|false => limits data extraction to 15 customers
- --port int => specify the debugger port, by default 9222
- --load true|false => load customers from urls.txt instead of parsing online, by default false