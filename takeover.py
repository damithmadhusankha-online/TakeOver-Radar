import argparse
import sys
import os
import urllib3
import requests
import dns.resolver
from concurrent.futures import ThreadPoolExecutor
from rich.console import Console
from rich.table import Table
from rich.progress import track

#To Remove HTTPS Certificate Warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

console = Console()

# 25+ Powerful Subdomain Takeover Fingerprints
FINGERPRINTS = {
    "GitHub Pages": "There isn't a GitHub Pages site here",
    "Heroku": "No such app",
    "Vercel": "The deployment could not be found",
    "AWS S3": "The specified bucket does not exist",
    "Shopify": "Sorry, this shop is currently unavailable",
    "Tumblr": "Whatever you were looking for doesn't exist",
    "Squarespace": "Squarespace - Website Not Found",
    "Ghost": "The thing you were looking for is no longer here",
    "Bitbucket": "Repository not found",
    "Fastly": "Fastly error: unknown domain",
    "Pantheon": "The Gods are wise, but you are lost",
    "Basecamp": "The page you looking for can't be found",
    "UserVoice": "This UserVoice subdomain does not exist",
    "Surge.sh": "project not found",
    "Intercom": "This page is reserved for artistic layouts",
    "Zendesk": "Help Center Closed",
    "Readme.io": "Project doesnt exist",
    "Wix": "Looks like this domain is not connected to a website",
    "Fly.io": "404 Not Found - Fly.io",
    "SmartJobBoard": "This job board website is either expired or its domain name is invalid",
    "Pingdom": "Public Backpage Not Found",
    "Tilda": "Domain has been assigned",
    "Firebase": "Site Not Found",
    "Cloudfront": "Bad Gateway: CloudFront attempted to establish a connection",
    "CargoCollective": "404 Not Found - Cargo Collective"
}

def get_cname(domain):
    
    try:
        answers = dns.resolver.resolve(domain, 'CNAME')
        for rdata in answers:
            return str(rdata.target).strip('.')
    except Exception:
        return None

def check_subdomain(subdomain):
    
    subdomain = subdomain.strip().lower()
    if not subdomain:
        return None

    # 1. DNS Verification
    cname = get_cname(subdomain)
    
    # 2. HTTP Verification
    url = f"http://{subdomain}"
    try:
        response = requests.get(url, timeout=5, verify=False, allow_redirects=True)
        html_content = response.text

        for service, fingerprint in FINGERPRINTS.items():
            if fingerprint.lower() in html_content.lower():
                return {
                    "subdomain": subdomain, 
                    "status": "VULNERABLE", 
                    "service": service, 
                    "cname": cname or "N/A"
                }
                
        return {"subdomain": subdomain, "status": "Safe", "service": "N/A", "cname": cname or "N/A"}
    except requests.exceptions.RequestException:
        return {"subdomain": subdomain, "status": "Dead/Error", "service": "N/A", "cname": cname or "N/A"}

def main():
    # Ultimate Branding Banner
    console.print("\n[bold cyan]╔══════════════════════════════════════════════════════════════╗[/bold cyan]")
    console.print("[bold cyan]║               ⚡ TAKEOVER-RADAR ULTIMATE v1.0 ⚡             ║[/bold cyan]")
    console.print("[bold white]║          Advanced Multi-threaded Subdomain Scanner           ║[/bold white]")
    console.print("[bold white]║                Developed By Damith Madhusankha               ║[/bold white]")
    console.print("[bold dim cyan]╚══════════════════════════════════════════════════════════════╝[/bold dim cyan]\n")

    parser = argparse.ArgumentParser(description="Takeover-Radar: Subdomain Takeover Scanner")
    parser.add_argument("-f", "--file", required=True, help="Subdomains wordlist file (.txt)")
    parser.add_argument("-t", "--threads", type=int, default=25, help="Number of concurrent threads (Default: 25)")
    parser.add_argument("-o", "--output", default="vulnerable_results.txt", help="Output file to save vulnerable domains")
    args = parser.parse_args()

    if not os.path.exists(args.file):
        console.print(f"[bold red][!] Error: '{args.file}' File Not Found![/bold red]")
        sys.exit(1)

    with open(args.file, "r") as f:
        subdomains = [line.strip() for line in f.readlines() if line.strip()]

    console.print(f"[yellow][*] Targets Loaded: {len(subdomains)} | Active Threads: {args.threads}[/yellow]")
    console.print("[yellow][*] Scanning Started...Please Wait...[/yellow]\n")

    results = []
    vulnerable_list = []
    
    
    with ThreadPoolExecutor(max_workers=args.threads) as executor:
        futures = [executor.submit(check_subdomain, sub) for sub in subdomains]
        
        # Rich Beautiful Progress Bar
        for future in track(futures, description="[cyan]Scanning...[/cyan]"):
            res = future.result()
            if res:
                results.append(res)
                if res["status"] == "VULNERABLE":
                    vulnerable_list.append(res)

    # Output Table 
    table = Table(title="\n📊 SCAN SUMMARY REPORT", title_style="bold magenta")
    table.add_column("Subdomain", justify="left", style="cyan")
    table.add_column("Status", justify="center")
    table.add_column("Service Detected", justify="left", style="green")
    table.add_column("CNAME Record", justify="left", style="yellow")

    for res in results:
        if res["status"] == "VULNERABLE":
            status_text = "[bold pulse white on red] VULNERABLE [/bold pulse white on red]"
        elif res["status"] == "Safe":
            status_text = "[green]Safe[/green]"
        else:
            status_text = "[dim white]Dead/Error[/dim white]"

        table.add_row(res["subdomain"], status_text, res["service"], res["cname"])

    console.print(table)
    
    
    if vulnerable_list:
        with open(args.output, "w") as out_file:
            out_file.write(f"=== TAKEOVER-RADAR REPORT ===\n")
            for vuln in vulnerable_list:
                out_file.write(f"[+] Vulnerable: {vuln['subdomain']} | Service: {vuln['service']} | Cname: {vuln['cname']}\n")
        
        console.print(f"\n[bold red][🔥] ALERT: Vulnerable Subdomain {len(vulnerable_list)} Found![/bold red]")
        console.print(f"[bold green][➔] All Details Saved To '{args.output}' file. [/bold green]\n")
    else:
        console.print("\n[bold green][✔] Scan Successful. Vulnerable - Not Found!. Safe![/bold green]\n")

if __name__ == "__main__":
    main()