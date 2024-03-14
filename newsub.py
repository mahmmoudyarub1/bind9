import os
import re
import mysql.connector

def subdomain_exists_in_zone(zone_file_path, subdomain_name):
    with open(zone_file_path, 'r') as zone_file:
        for line in zone_file:
            if line.startswith(f'{subdomain_name} '):
                return True
    return False

def add_subdomain(zone_name, subdomain_name, ip_address):
    # Step 1: Open the existing zone file associated with the domain
    zone_file_path = f'/etc/bind/zones/{zone_name}.db'

    # Step 2: Check if the subdomain already exists in the zone file
    if subdomain_exists_in_zone(zone_file_path, subdomain_name):
        print(f"Subdomain '{subdomain_name}' already exists in zone '{zone_name}'. Skipping...")
        return

    # Step 3: Add the necessary records for the new subdomain
    with open(zone_file_path, 'a') as zone_file_append:
        # Ensure that each record ends with a newline character
        zone_file_append.write(f'{subdomain_name}  IN      A       {ip_address}\n')

    # Step 4: Update the serial number in the SOA record
    with open(zone_file_path, 'r+') as zone_file:
        lines = zone_file.readlines()
        for i, line in enumerate(lines):
            if line.startswith('@') and 'IN SOA' in line:
                parts = re.split(r'\s+', line)
                serial_index = parts.index('Serial')
                serial = int(parts[serial_index + 1].rstrip(';'))  # Extract the serial number
                serial += 1  # Increment the serial number
                parts[serial_index + 1] = str(serial)  # Update the serial number
                lines[i] = ' '.join(parts) + '\n'
                break

    # Write the updated lines back to the file
    with open(zone_file_path, 'w') as zone_file:
        zone_file.writelines(lines)

    # Step 5: Restart BIND9 service
    os.system('service bind9 restart')

def get_subdomain_info_from_database():
    # Connect to the database
    connection = mysql.connector.connect(
        host='localhost',
        user='root',
        password='pass',
        database='dns'
    )

    try:
        # Create a cursor object to execute queries
        cursor = connection.cursor()

        # Execute the query to fetch subdomain information
        cursor.execute("SELECT zone_name, subdomain_name, ip_address FROM subdomains")

        # Fetch all rows from the result set
        subdomain_info = cursor.fetchall()

    finally:
        # Close the database connection
        connection.close()

    return subdomain_info

# Usage
if __name__ == "__main__":
    subdomain_info = get_subdomain_info_from_database()
    for zone_name, subdomain_name, ip_address in subdomain_info:
        add_subdomain(zone_name, subdomain_name, ip_address)
