import os
import CONFIG
import os
import shutil
import requests


def remove(path):
    """ param <path> could either be relative or absolute. """
    if os.path.isfile(path) or os.path.islink(path):
        os.remove(path)  # remove the file
    elif os.path.isdir(path):
        shutil.rmtree(path)  # remove dir and all contains
    
def download_rtc_attachment(url,rtcclient,relativefilepathandname):

    invalid = '<>:"|?* '
    for char in invalid:
        relativefilepathandname = relativefilepathandname.replace(char, '')
        
    headers = rtcclient.headers
    headers['Accept']='text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9'

    file = requests.get(url,headers=headers,allow_redirects=True,verify=False)
    with open(relativefilepathandname, 'wb') as f:
        f.write(file.content);


