import subprocess, sys, os
from bs4 import BeautifulSoup
import shutil, re
from git import Repo

os.chdir('site')
folder_path = os.getcwd()

def main_build_doc():
    folder_path=sys.argv[1]
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
    

def delete_branch(folder_path):
    gh_pages_branche_name = "gh-pages"
    repo = Repo(folder_path)
    if gh_pages_branche_name != repo.active_branch.name:
        repo.index.add("*")
        repo.index.commit("Commit avant mise en ligne site")
        repo.git.push()
    repo.git.checkout(gh_pages_branche_name)
    repo.git.rm('-r', '*')
    repo.git.push('origin', gh_pages_branche_name)
    repo.delete_head(gh_pages_branche_name, force=True)
    repo.git.push('origin', '--delete', gh_pages_branche_name)

def create_gh_pages_branch_from_site_dir(folder_path):
    gh_pages_branche_name = "gh-pages"
    os.chdir(folder_path)
    subprocess.run(['git', 'subtree', 'split', '--prefix', "_build/html", '--branch', gh_pages_branche_name])
    subprocess.run(['git', 'push', 'origin', gh_pages_branche_name])


def add_jv_control(folder_path):
    path = os.path.join(folder_path, "_build", "html")
    for r, d, f in os.walk(path):
        for file in f:
            file_path = os.path.join(r, file)
            if (file_path.endswith('.html')) & (re.search(r"\\_static\\|\\_sources\\|\\_sphinx_design_static\\", file_path) is None):
                print(file_path)
                # Lire le fichier HTML
                print(file_path)
                with open(file_path, 'r') as f:
                    contents = f.read()
                    soup = BeautifulSoup(contents, 'html.parser')
                    p_tags = soup.find('body')
                    p_tags.append("""<script>
                            if (!localStorage.getItem('mdp')) {
                                window.location.href = "../index.html";
                            }
                        </script>
                        """)
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
