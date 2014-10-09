import os,shutil
import subprocess as sp
import cherrypy
from string import Template

PWD = os.path.abspath(os.getcwd())
DOSSIER = os.path.join('lib','plugins','gregorio')
with open(os.path.join(DOSSIER,'saisie.html')) as f:
    SAISIE = Template(f.read(-1)).substitute(nom = os.path.splitext(os.path.basename(__file__))[0])
with open(os.path.join(DOSSIER,'style.css')) as f:
    CSS = f.read(-1)

def accueillir(*arguments,**parametres):
    with open("log",'a') as f:
        f.write('arguments : {0}\n'.format(str(arguments)))
        f.write('paramètres : {0}\n'.format(str(parametres)))
    try:
        return{'traiter': traiter(parametres['texte'])}[arguments[0]]
    except KeyError: return SAISIE

def traiter(contenu):
    modele = 'gregorio'
    fichier = 'partition.gabc'
    commande = ['lualatex','-interaction=batchmode','--shell-escape','partition']
    destination = os.path.join('tmp',modele)
    environnement = os.environ.copy()
    environnement['TEXINPUTS'] = 'lib:'
    shutil.rmtree(destination,True)
    shutil.copytree(
        os.path.join('modeles',modele),
        destination
        )
    os.chdir(destination)
    with open(os.path.join('gabc',fichier),'w') as f:
        f.write(contenu)
    with open('Gabarit.tex','r') as g:
        with open('partition.tex','w') as f:
            f.write(
                g.read(-1) % {
                    'papier': 'a5paper',
                    'police': '12',
                    }
                )
    sortie,erreurs = sp.Popen(commande,env=environnement,stdout=sp.PIPE,stderr=sp.PIPE).communicate()
    os.chdir(PWD)
    return {'dossier':destination,'fichier':'partition.pdf'}



'''
def POST(self,url='gregorio',texte=''):
        sortie = PLUGINS[cherrypy.session['plugin']].traiter(texte)
        os.renames(os.path.join(sortie['dossier'],sortie['fichier']),os.path.join('static','files',cherrypy.session['plugin'],sortie['fichier']))
        return Page(
            '<object type="application/pdf" data="/static/files/{0}/{1}" zoom="page" width="100%" height="100%"></object>'.format(
                cherrypy.session['plugin'],sortie['fichier']
                )
            ).contenu
'''
