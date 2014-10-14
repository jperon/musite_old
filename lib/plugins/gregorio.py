import os,shutil
import subprocess as sp
from string import Template
import config as c, jrnl as l
import outils as s, auth as a, gabctk as g
import cherrypy as cp

NOM = 'gregorio'
EXT = 'gabc'
DOSSIER = os.path.join('lib','plugins','gregorio')

def css():
    with open(os.path.join(DOSSIER,'style.css')) as f: return f.read(-1)


def retourner(*arguments,**parametres):
    l.log('arguments : {}\n paramètres : {}\n'.format(str(arguments),str(parametres)))
    try:
        return {
            'saisir': saisir,
            'traiter': traiter,
            }[arguments[0]](parametres)
    except (KeyError,IndexError):
        return accueillir()

def arborescence(dossier,generateur):
    for d in dossier:
        pass

@s.page
def accueillir():
    dossier = os.path.join(c.DATA,EXT)
    dossiers = os.walk(dossier)
    structure = '\n'.join(
        ['<b>{0}</b>\n<ul>\n\t<li>{1}</li>\n</ul>'.format(
            d[0].replace(dossier + os.sep,''),
            '</li>\n\t<li>'.join(d[2])
            )
        for d in dossiers if len(d[2])]
        )
    l.log(structure)
    return structure

@s.page
def saisir(parametres):
    with open(os.path.join(DOSSIER,'saisie.html')) as f, open(os.path.join(DOSSIER,'piece.gabc')) as g:
            return Template(f.read(-1)).substitute(
                nom = NOM,
                texte = g.read(-1),
                )

def traiter(parametres):
    return {'compiler':compiler,
    'enregistrer':enregistrer,
    }[parametres['action']](parametres)

@s.page
def compiler(parametres):
    contenu = parametres['texte']
    fichier = 'partition.gabc'
    commande = ['lualatex','-interaction=batchmode','--shell-escape','partition']
    destination = os.path.join(c.TMP,NOM)
    environnement = os.environ.copy()
    environnement['TEXINPUTS'] = 'lib:'
    shutil.rmtree(destination,True)
    shutil.copytree(
        os.path.join('modeles',NOM),
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
    os.chdir(c.PWD)
    os.renames(os.path.join(destination,'partition.pdf'),os.path.join('static','fichiers','pdf','partition.pdf'))
    return '<object type="application/pdf" data="/static/fichiers/{0}/{1}" zoom="page" width="100%" height="100%"></object>'.format(
                'pdf','partition.pdf'
                )

def enregistrer(parametres):
    gabc = g.Gabc(parametres['texte'])
    dossier = os.path.join(c.DATA,EXT,gabc.entetes['office-part'])
    os.makedirs(dossier,exist_ok=True)
    fichier = gabc.entetes['name'].replace(' ','_').lower() + '.' + EXT
    with open(os.path.join(dossier,fichier),'w') as f:
        f.write(parametres['texte'])
    raise(cp.HTTPRedirect('/' + NOM))
