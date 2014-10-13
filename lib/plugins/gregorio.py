import os,shutil
import subprocess as sp
from string import Template
import outils as s, auth as a, gabctk as g
import cherrypy as cp

NOM = __name__
PWD = os.path.abspath(os.getcwd())
DOSSIER = os.path.join('lib','plugins','gregorio')

def css():
	with open(os.path.join(DOSSIER,'style.css')) as f: return f.read(-1)


def retourner(*arguments,**parametres):
    with open("log",'a') as f:
        f.write('arguments : {0}\n'.format(str(arguments)))
        f.write('paramètres : {0}\n'.format(str(parametres)))
    try:
        return{'traiter': traiter(parametres)}[arguments[0]]
    except (KeyError,IndexError):
        return accueillir()

@s.page
def accueillir():
    with open(os.path.join(DOSSIER,'saisie.html')) as f, open(os.path.join(DOSSIER,'piece.gabc')) as g:
            return Template(f.read(-1)).substitute(
                nom = NOM,
                texte = g.read(-1),
                )


def traiter(parametres):
    return {'compiler':compiler(parametres['texte']),
    'enregistrer':enregistrer(parametres['texte']),
    }[parametres['action']]

@s.page
def compiler(contenu):
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
    os.renames(os.path.join(destination,'partition.pdf'),os.path.join('static','files',NOM,'partition.pdf'))
    return '<object type="application/pdf" data="/static/files/{0}/{1}" zoom="page" width="100%" height="100%"></object>'.format(
                NOM,'partition.pdf'
                )

@s.page
def enregistrer(texte):
    gabc = g.Gabc(texte)
    return gabc.entetes
    #raise(cp.HTTPRedirect('/' + NOM))
