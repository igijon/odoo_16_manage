from os import path
from os import remove


def delete_file(file):
    if path.exists(file):
        remove(file)

def write_text(text, file):
    with open(file, 'a') as f:
        f.write(text)

def write_dev(line, demo_file):
    write_text(f'<record id=\'dev_{line[0]}\' model=\'res.partner\'>', demo_file)
    write_text(f'<field name=\'name\'>{line[1]}</field>', demo_file)
    write_text(f'<field name=\'access_code\'>{line[2]}</field>', demo_file)
    write_text(f'<field name=\'is_dev\'>True</field>', demo_file)
    write_text(f'</record>', demo_file)


def devs_generator(source, demo_file):
    delete_file(demo_file)
    write_text('<odoo><data>', demo_file)
    with open(source) as file:
        for line in file:
            line = line.split(',')
            write_dev(line, demo_file)
    write_text('</data></odoo>', demo_file)


devs_generator('devs.csv', 'demo/devs.xml')