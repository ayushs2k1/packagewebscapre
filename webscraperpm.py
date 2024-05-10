import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import urllib.parse
import re

def get_latest_version(package_name):
    url = f"https://rpmfind.net/linux/rpm2html/search.php?query=+{package_name}+&submit=Search"
    if not url:
        return "URL not found", None

    headers = {
        "User-Agent": "Chrome/58.0.3029.110"
    }

    for _ in range(10):
        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                break
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            time.sleep(10)
    else:
        print("Failed to fetch data after 10 retries")
        return "Error fetching data", None

    print(f"URL: {response.url}")
    print(f"HTTP Status Code: {response.status_code}")

    soup = BeautifulSoup(response.content, 'html.parser')

    # Find all package entries
    package_entries = soup.find_all("tr")

    if not package_entries:
        return "No package entries found", None

    # Filter package entries for CentOS 8-stream BaseOS for x86_64
    centos_packages = [pkg for pkg in package_entries if pkg.find("a") and pkg.find("a")["href"].endswith("el8.x86_64.html")]

    if not centos_packages:
        return "No CentOS 8-stream BaseOS for x86_64 entries found", None
    
    # Extract the latest package entry
    latest_package_entry = centos_packages[0]
    
    # Extract package name and version from the entry
    package_link = latest_package_entry.find_all("a")[1]

    if package_link:
        package_full_name = package_link.text.strip()
        print(f"Package Full Name: {package_full_name}")
        download_link = urllib.parse.urljoin(url, package_link.get("href"))
        print(f"Download Link: {download_link}")
    else:
        return "Package not found", None

    return package_full_name, download_link

def process_packages(input_file):
    # Read input packages from Excel file
    df = pd.read_excel(input_file)

    # Create an empty list to store the results
    results = []

    # Iterate through each row in the DataFrame
    for index, row in df.iterrows():
        package_name = row['Package']

        match = re.match(r"^([a-zA-Z0-9_.+-]+?)(?=-\d)", package_name)
        if match:
            package_name = match.group(1)

        # Get the latest version and URL for the package
        latest_version, url = get_latest_version(package_name)

        # Append the results to the list
        results.append({
            "File": row['File'],
            "Package": row['Package'],
            "Vendor": row['Vendor'],
            "URL": row['URL'],
            "License": row['License'],
            "Latest Version": latest_version,
            "Download Link": url
        })

    # Create a DataFrame from the results
    result_df = pd.DataFrame(results)

    # Generate the output file name based on the input file name
    # output_file = input_file.replace(".xlsx", "_output.xlsx")

    # Write the results to the output Excel file
    result_df.to_excel(input_file, index=False)

    print(f"Results saved to {input_file}")

def main():

    process_packages("consolidated_distroless_base_new.xlsx")

if __name__ == "__main__":
    main()
