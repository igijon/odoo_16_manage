from os import path
from os import remove
import base64

def random_technologies():
    n_t = random.randint(1, n_technologies+1)
    cont = 0
    tech = []
    while cont < n_t:
        t = random.randint(1, n_technologies+1)
        tech_id = "technology_"+str(t)
        if not tech_id in tech:
            tech.append(tech_id)
            cont += 1
    return tech

def delete_file(file):
    if path.exists(file):
        remove(file)

def write_text(text, file):
    with open(file, 'a') as f:
        f.write(text)

def write_dev(line, demo_file):
    write_text(f'<record id=\'dev_{line[0]}\' model=\'res.partner\'>', demo_file)
    write_text(f'<field name=\'name\'>{line[1]}</field>', demo_file)
    write_text(f'<field name=\'last_login\' eval=\"(datetime.now().strftime(\'%Y-%m-%d\'))\"></field>', demo_file)
    write_text(f'<field name=\'access_code\'>{line[2]}</field>', demo_file)
    write_text(f'<field name=\'is_dev\'>True</field>', demo_file)
    write_text(f'</record>', demo_file)

def write_project(line, demo_file):
    write_text(f'<record id=\'project_{line[0]}\' model=\'manage.project\'>', demo_file)
    write_text(f'<field name=\'name\'>{line[1]}</field>', demo_file)
    write_text(f'</record>', demo_file)

def write_history(line, demo_file):
    write_text(f'<record id=\'history_{line[0]}\' model=\'manage.history\'>', demo_file)
    write_text(f'<field name=\'name\'>{line[1]}</field>', demo_file)
    write_text(f'<field name=\'project\' ref=\'project_1\'></field>', demo_file)
    write_text(f'</record>', demo_file)

def write_technology(line, demo_file):
    write_text(f'<record id=\'technology_{line[0]}\' model=\'manage.technology\'>', demo_file)
    write_text(f'<field name=\'name\'>{line[1]}</field>', demo_file)
    image = open("dev_image/"+line[1].strip()+".png","rb")
    b64_string = base64.b64encode(image.read()).decode('utf-8')
    write_text(f'<field name=\'photo\'>{b64_string}</field>', demo_file)
    write_text(f'</record>', demo_file)

def devs_generator(source, demo_file):
    delete_file(demo_file)
    write_text('<odoo><data>', demo_file)
    with open(source) as file:
        for line in file:
            line = line.split(',')
            write_dev(line, demo_file)
    write_text('</data></odoo>', demo_file)

def projects_generator(source, demo_file):
    delete_file(demo_file)
    write_text('<odoo><data>', demo_file)
    with open(source) as file:
        for line in file:
            line = line.split(',')
            write_project(line, demo_file)
    write_text('</data></odoo>', demo_file)

def histories_generator(source, demo_file):
    delete_file(demo_file)
    write_text('<odoo><data>', demo_file)
    with open(source) as file:
        for line in file:
            line = line.split(',')
            write_history(line, demo_file)
    write_text('</data></odoo>', demo_file)

def technologies_generator(source, demo_file):
    delete_file(demo_file)
    write_text('<odoo><data>', demo_file)
    with open(source) as file:
        for line in file:
            line = line.split(',')
            write_technology(line, demo_file)
    write_text('</data></odoo>', demo_file)


devs_generator('devs.csv', 'demo/devs.xml')
projects_generator('projects.csv', 'demo/projects.xml')
histories_generator('histories.csv', 'demo/histories.xml')
technologies_generator('technologies.csv', 'demo/technologies.xml')