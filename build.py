import subprocess, sys, os
from bs4 import BeautifulSoup
import shutil, re

def main_build_doc():
    subprocess.run(["git", "config", "--global", "core.autocrlf", "false"])
    folder_path=sys.argv[1]
    gh_pages_branche_name = "gh-pages"
    os.chdir(folder_path)
    try:
        shutil.rmtree(os.path.join(folder_path, "_build"))
    except:
        pass
    subprocess.run(["jupyter-book", "build", "."])
    add_jv_control(folder_path)
    change_folder(folder_path)
    add_password_page(folder_path)
    with open(os.path.join(folder_path, "_build", "html", ".nojekyll"), "w") as f:
        pass
    delete_branch(gh_pages_branche_name)
    create_gh_pages_branch_from_site_dir(gh_pages_branche_name)

def git_checkout(command, block=True):
    try:
        output = subprocess.check_output(command, stderr=subprocess.STDOUT)
        print("Commande exécutée avec succès :\n", output.decode())
        
    except subprocess.CalledProcessError as e:
        print("Une erreur est survenue pendant l'exécution de la commande git checkout :")
        if block:
            raise ValueError("Message d'erreur :", e.output.decode())
        else:
            print("Message d'erreur :", e.output.decode())


def delete_branch(gh_pages_branche_name):
    git_checkout(['git', 'add', '.'])
    git_checkout(['git', 'commit', '-m', "Commit avant mise en ligne site"])
    git_checkout(['git', 'push', 'origin', 'main', '--force'])
    try:
        git_checkout(["git", "checkout", gh_pages_branche_name])
    except:
        git_checkout(["git", "checkout", '-b', gh_pages_branche_name])
    git_checkout(['git', 'add', '.'], False)
    git_checkout(['git', 'commit', '-m', "Commit avant mise en ligne site"], False)
    git_checkout(['git', 'push', 'origin', gh_pages_branche_name, '--force'])
    git_checkout(["git", "rm", "-r", "*"], False)
    git_checkout(["git", "push", "origin", gh_pages_branche_name, '--force'])
    git_checkout(["git", "checkout", "main"])
    git_checkout(["git", "branch", "-D", gh_pages_branche_name])
    git_checkout(["git", "push", "origin", "--delete", gh_pages_branche_name])

def create_gh_pages_branch_from_site_dir(gh_pages_branche_name):
    git_checkout(['git', 'subtree', 'split', '--prefix', "_build/html", '--branch', gh_pages_branche_name])
    git_checkout(['git', 'push', 'origin', gh_pages_branche_name])


def add_jv_control(folder_path):
    path = os.path.join(folder_path, "_build", "html")
    for r, d, f in os.walk(path):
        for file in f:
            file_path = os.path.join(r, file)
            if (file_path.endswith('.html')) & (re.search(r"\\_static\\|\\_sources\\|\\_sphinx_design_static\\", file_path) is None):
                print(file_path)
                folders = r.split('\\')
                ifold=0
                while folders[ifold] != "html":
                    ifold+=1
                depth = len(folders)-ifold
                depth_string = ""
                for p in range(depth):
                    depth_string +="../"                                      
                with open(file_path, 'r') as f:
                    contents = f.read()
                    soup = BeautifulSoup(contents, 'html.parser')
                    tag = soup.new_tag("script")
                    tag.append("""
fetch('"""+depth_string+"""mdp.txt')
.then(response => response.text())
.then(mdp => {
    if ((!sessionStorage.getItem('mdp')) || (sessionStorage.getItem('mdp') != mdp))  {
        window.location.href = "../index.html"
    }
})
                        """)
                    soup.body.append(tag)
                # Écrire le HTML modifié dans le fichier
                with open(file_path, 'w') as f:
                    f.write(str(soup))

def change_folder(folder_path):
    new_path = os.path.join(folder_path, "_build", "html", "site")
    build_path = os.path.join(folder_path, "_build", "html")
    os.mkdir(new_path)
    for el in os.listdir(build_path):     
        if el != "site":
            shutil.move(os.path.join(build_path,el), new_path)

def add_password_page(folder_path):
    path_pw_page = os.path.join(folder_path, "index.html")
    path_pw = os.path.join(folder_path, "mdp.txt")
    build_path = os.path.join(folder_path, "_build", "html")
    shutil.copyfile(path_pw_page, os.path.join(build_path, "index.html"))
    shutil.copyfile(path_pw, os.path.join(build_path, "mdp.txt"))       


if __name__ == "__main__":
    main_build_doc()
