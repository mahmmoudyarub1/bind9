import os
import mysql.connector

def domain_exists_in_database(domain_name):
    connection = mysql.connector.connect(host='localhost',
                                         user='root',
                                         password='pass',
                                         database='dns')

    try:
        with connection.cursor() as cursor:
            sql = "SELECT COUNT(*) FROM zones WHERE domain_name = %s"
            cursor.execute(sql, (domain_name,))
            result = cursor.fetchone()
            if result[0] > 0:
                return True
            else:
                return False

    finally:
        connection.close()

def add_zone_and_domain(zone_name, domain_name, ip_address):

    if domain_exists_in_database(domain_name):
        print(f"Domain '{domain_name}' already exists. Skipping...")
        return


    named_conf_path = '/etc/bind/named.conf'
    with open(named_conf_path, 'a') as named_conf:
        named_conf.write(f'\nzone "{zone_name}" IN {{\n')
        named_conf.write(f'    type master;\n')
        named_conf.write(f'    file "/etc/bind/zones/{zone_name}.db";\n')
        named_conf.write(f'}};\n')


    zone_file_path = f'/etc/bind/zones/{zone_name}.db'
    with open(zone_file_path, 'w') as zone_file:
        zone_file.write(f'$TTL    604800\n')
        zone_file.write(f'@       IN      SOA     ns1.{domain_name}. root.{domain_name}. (\n')
        zone_file.write(f'                              2         ; Serial\n')
        zone_file.write(f'                         604800         ; Refresh\n')
        zone_file.write(f'                          86400         ; Retry\n')
        zone_file.write(f'                        2419200         ; Expire\n')
        zone_file.write(f'                         604800 )       ; Negative Cache TTL\n')
        zone_file.write(f'@       IN      NS      ns1.{domain_name}.\n')
        zone_file.write(f'@       IN      A       {ip_address}\n')
        zone_file.write(f'ns1     IN      A       {ip_address}\n')


    os.system('service bind9 restart')


def get_domain_info_from_database():
    connection = mysql.connector.connect(host='localhost',
                                         user='root',
                                         password='pass',
                                         database='dns')

    try:
        with connection.cursor() as cursor:
            sql = "SELECT zone_name, domain_name, ip_address FROM zones"
            cursor.execute(sql)
            result = cursor.fetchall()

    finally:
        connection.close()

    return result


if __name__ == "__main__":
    domain_info = get_domain_info_from_database()
    for zone_name, domain_name, ip_address in domain_info:
        add_zone_and_domain(zone_name, domain_name, ip_address)
