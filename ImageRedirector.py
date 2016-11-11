from requests.packages import urllib3
import subprocess,os
import shutil

urllib3.disable_warnings()

def image_redirector(filetocheck):

# Variables del ambiente,
# filetocheck tiene el path completo del archivo a revisar
# path_to_file tendra el directorio donde esta el archivo
# html_file_name tiene el nombre del archivo a revisar

    path_to_file = filetocheck
    while path_to_file[-1] != '/':
        path_to_file = path_to_file[0:-1]
    html_file_name = filetocheck.split('/')[-1]
    numbers = '1234567890' # es para una validacion por caracteres nomas dejar aca

# Barrido del archivo inicial
# la logica aca es la siguiente, se abre el archivo que viene de TreeCheck y se crea el archivo
# exctracted_urls. El script recorre linea por linea buscando las que tienen coincidencias con showImage.asp
# si encuentra recorta la linea y extrae los siguientes datos.
# url = la url completa del objeto
# original_name = el nombre original del objeto (con el querystring)
# new_name = se forma con el querystring + .png
# new_url = se forma con la url original a la que se le reemplaza el original_name con el new_name
# estos cuatro datos van al archivo exctracted_urls.txt como vectores y se obtiene un listado de todos los
# llamados que se hacen al showImage.asp, los objetos y los nuevos llamados

    f = open(filetocheck,'r')
    g = open('exctracted_urls.txt', 'w')

    while (True):
        line = f.readline()

        if 'showImage.asp' in line:
            line = line.split(' ')
            for x in line:
                if 'showImage.asp' in x:
                    url = x.replace('src=','').replace('"','').replace("'",'')
                    while url[-1] not in numbers:
                        url = url[0:-1]
                    original_name = str(url.split('/')[-1])
                    new_name = str(url.split('?')[-1] + '.png')
                    new_url = url.replace(original_name,new_name)
                    g.write(url + ',' + original_name + ',' + new_name + ',' + new_url + '\n')

        if line == '':
            #print "EoF reached...."
            f.close()
            g.close()
            break

# Bajada de las imagenes
# la logica aca es la siguiente, se abre exctracted_urls
# El script recorre levanta las lineas del archivo y las secciona del 0 al 3
# 0 = url = la url completa del objeto
# 1 = original_name = el nombre original del objeto (con el querystring)
# 2 = new_name = se forma con el querystring + .png
# 3 = new_url = se forma con la url original a la que se le reemplaza el original_name con el new_name
# Se le hace un curl al 0, se renombra el archivo obtenido por el path de las imagenes + el 2

    g = open('exctracted_urls.txt', 'r')
    while (True):

        line = g.readline()
        img_url = line.split(',')

        if img_url[0] == '':
            g.close()
            break

        cmd = 'curl -O ' + img_url[0]

        subprocess.check_output([cmd], shell=True)
        os.rename(img_url[1], 'output/' + filetocheck.split('/')[2] + '/' + img_url[3].split('/')[2] + '/scripts/' + img_url[2])

        print img_url[1] + ' >> ' + 'output/' + filetocheck.split('/')[2] + '/' + img_url[3].split('/')[2] + '/scripts/' + img_url[2]
        #os.rename(img_url[1], "www.santander.com.uy/scripts/"+img_url[2])

    g.close()

# Reescritura del archivo original
# la logica aca es la siguiente, se abre el archivo original y un archivo temporal index.html.tmp
# El script transcribe las lineas del archivo original al temporal, hasta que encuentra una coincidencia
# con showImage.asp, dado que pueden haber varias coincidencias en la misma linea entra en un loop
# que trabaja de la siguiente forma:
# abre exctracted_urls.txt y busca coincidencias con la url completa img_url[0], si coincide reemplaza
# por la url nueva img_url[3] sin el \n sino sigue buscando. Cuando ya no hay coincidencias con showImage.asp
# transcribe la nueva linea modificada al archivo.
# cuando termina la transcripcion, el archivo temporal se mueve y renombra al directorio correspondiente (path_to_file)
# con el nombre correspondiente (html_file_name) y sale del bucle

    while (True):

        f1 = open(filetocheck, 'r')
        f2 = open('index.html.tmp', 'w')
        for line in f1:
            if 'showImage.asp' in line:
                g = open('exctracted_urls.txt', 'r')
                lineg = g.readline()
                while ('showImage.asp' in line):
                    img_url = lineg.split(',')
                    if img_url[0] in line:
                        line = line.replace(img_url[0], img_url[3].replace('\n',''))
                    else:
                        lineg = g.readline()
            f2.write(line)
        os.rename('index.html.tmp', path_to_file + html_file_name)
        break

    f1.close()
    f2.close()
    return


# Relevamiento de archivos html, las rutas y los archivos html se guardaran en html_files.txt
# Solo quedaran anotados los html que tienen requests a showImage.asp

h = open('html_files.txt', 'w')
for root, dirs, files in os.walk("./output", topdown=False):
    for name in files:
        if '.html' in name:
            path_to_file = os.path.join(root, name)
            file = open(path_to_file,'r')
            while(True):
                line = file.readline()
                if 'showImage.asp' in line:
                    h.write(path_to_file + '\n')
                    file.close()
                    break
                if line == '':
                    file.close()
                    break
            #print path_to_file
h.close()

# llamado al ImageRedirector, para cada uno de los archivos listados en html_files.txt se
# hara un llamado al ImageRedirector pasando como parametro el path completo al archivo SIN el \n

fopen = open('html_files.txt', 'r')
line = fopen.readline()
while(True):
    line = fopen.readline()
    if line == '':
        break
    print "\nWorking on: " + line.replace('\n','')
    image_redirector(line.replace('\n',''))

fopen.close()

# Recorre el arbol de directorios si encuentra un archivo con ".html" (el punto es importante, si un archivo
# tuviera "html" en el cuerpo del nombre tambien lo reemplazaria), crea una copia y le cambia la extension

for root, dirs, files in os.walk("./output", topdown=False):
    for name in files:
        if '.html' in name:
            path_to_file = os.path.join(root, name)
            file_name = name.replace('.html', '.asp').replace('\n', '')
            while path_to_file[-1] != '/':
                path_to_file = path_to_file[0:-1]
            #print path_to_file + name + ' >> ' + path_to_file[2:] + file_name
            shutil.copy2(path_to_file[2:] + name, path_to_file[2:] + file_name)

print "\n\nWork completed..."