import gc
import os

def get_as_json(url):
    import urequests
    import json
    headers = {"User-Agent": "micropython"}
    r = urequests.get(url, headers=headers)
    return json.loads(r.text)

def github_sha_of_tag(github_repo, tag_name):
    latest_tag = None
    tags = get_as_json("https://api.github.com/repos/{}/tags".format(github_repo))
    for tag in tags:
        if tag["name"] == tag_name:
            latest_tag = tag
            break
            
    try:
        latest_sha = latest_tag["commit"]["sha"]
    except KeyError as e:
        raise ValueError(
            "Release not found: \n",
            "Please ensure release as marked as 'latest', rather than pre-release \n",
            "github api message: \n {} \n ".format(latest_tag)
        )
    #latest_release.close()
    return latest_sha

# different micropython versions act differently when directory already exists
def _mkdir(path:str):
    import os
    try:
        os.mkdir(path)
    except OSError as exc:
        if exc.args[0] == 17: 
            pass
        
def _rmtree(d):
    if os.stat(d)[0] & 0x4000:  # Dir
        for f in os.ilistdir(d):
            if f[0] not in ('.', '..'):
                _rmtree("/".join((d, f[0])))  # File or Dir
        os.rmdir(d)
    else:  # File
        os.remove(d)

def github_clone(github_repo, sha, target_dir):
    
    download_dir = "next"
    
    from httpclient import HttpClient

    headers = {}
    http_client = HttpClient(headers=headers)
    
    def _download_all_files(sha, sub_dir=''):
        url = 'https://api.github.com/repos/{}/contents/{}?ref={}'.format(github_repo, sub_dir, sha)
        gc.collect() 
        file_list = http_client.get(url)
        file_list_json = file_list.json()
        for file in file_list_json:
            path = "{}/{}".format(download_dir, file['path'])
            if file['type'] == 'file':
                gitPath = file['path']
                print('\tDownloading: ', gitPath, 'to', path)
                _download_file(sha, gitPath, path)
            elif file['type'] == 'dir':
                print('Creating dir', path)
                _mkdir(path)
                _download_all_files(sha, sub_dir + '/' + file['name'])
            gc.collect()

        file_list.close()

    def _download_file(sha, gitPath, path):
        http_client.get('https://raw.githubusercontent.com/{}/{}/{}'.format(github_repo, sha, gitPath), saveToFile=path)
        
    _download_all_files(sha)
    
def write_version(target_dir, sha):
    f = open("{}/VERSION.txt".format(target_dir), "wb")
    f.write(sha)
    f.close()
    
def read_version(target_dir):
    f = open("{}/VERSION.txt".format(target_dir), "rb")
    s = f.read().decode("utf-8")
    f.close()
    return s
    
# download update and replace target_dir with update
def download_and_apply_update(github_repo, tag_name, target_dir):
    temp_dir = "next"
    old_dir = "old"
    
    sha = github_sha_of_tag(github_repo, tag_name) 
    _mkdir(temp_dir)
    github_clone(github_repo, sha, temp_dir)
    write_version(temp_dir, sha)
    
    # cheapo check if dir exists. only works if target_dir is in the root
    if target_dir in os.listdir():
        if old_dir in os.listdir():
            _rmtree(old_dir)
        os.rename(target_dir, old_dir)
    os.rename(temp_dir, target_dir)
    
# return True if there is an update (or if target_dir doesn't exist, which is a special case for the first download)
def check_if_has_update(github_repo, tag_name, target_dir):
    sha = github_sha_of_tag(github_repo, tag_name)
    # purpose of try/catch is to catch the 
    try:
        current_sha = read_version(target_dir)
        print(sha, current_sha)
        return sha != current_sha
    except Exception as e:
        print(e)
        return True
