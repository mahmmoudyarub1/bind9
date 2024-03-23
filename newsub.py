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
    zone_file_path = f'/etc/bind/zones/{zone_name}.db'

    if subdomain_exists_in_zone(zone_file_path, subdomain_name):
        print(f"Subdomain '{subdomain_name}' already exists in zone '{zone_name}'. Skipping...")
        return

    with open(zone_file_path, 'a') as zone_file_append:
        zone_file_append.write(f'{subdomain_name}  IN      A       {ip_address}\n')

    with open(zone_file_path, 'r+') as zone_file:
        lines = zone_file.readlines()
        for i, line in enumerate(lines):
            if line.startswith('@') and 'IN SOA' in line:
                parts = re.split(r'\s+', line)
                serial_index = parts.index('Serial')
                serial = int(parts[serial_index + 1].rstrip(';'))  
                serial += 1  
                parts[serial_index + 1] = str(serial)  
                lines[i] = ' '.join(parts) + '\n'
                break

    with open(zone_file_path, 'w') as zone_file:
        zone_file.writelines(lines)


    os.system('service bind9 restart')

def get_subdomain_info_from_database():

    connection = mysql.connector.connect(
        host='localhost',
        user='root',
        password='pass',
        database='dns'
    )

    try:

        cursor = connection.cursor()


        cursor.execute("SELECT zone_name, subdomain_name, ip_address FROM subdomains")


        subdomain_info = cursor.fetchall()

    finally:

        connection.close()

    return subdomain_info


if __name__ == "__main__":
    subdomain_info = get_subdomain_info_from_database()
    for zone_name, subdomain_name, ip_address in subdomain_info:
        add_subdomain(zone_name, subdomain_name, ip_address)
