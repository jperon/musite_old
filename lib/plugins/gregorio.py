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
        return eval(arguments[0])(parametres)
    except (KeyError,IndexError):
        return accueillir()

@s.page
def accueillir():
    def titregabc(f):
        try:
            entetes = g.Gabc(g.FichierTexte(f).contenu).entetes
        except UnicodeDecodeError: return '''<b><i>Erreur d'encodage : {}</i></b>'''.format(f)
        if 'name' in entetes: return entetes['name']
        else: return '<b><i>À corriger : fichier sans balise "name" : {}</i></b>'.format(f)
    dossier = os.path.join(c.DATA,EXT)
    dossiers = os.walk(dossier)
    structure = '\n'.join(
        ['<b>{0}</b>\n<ul>\n\t<li>{1}</li>\n</ul>'.format(
            d[0].replace(dossier + os.sep,'').capitalize(),
            '</li>\n\t<li>'.join(
                '<a href="/gregorio/editer/?fichier={0}">{1}</a>'.format(
                    os.path.join(d[0].replace(dossier + os.sep,''),fichier),
                    titregabc(os.path.join(d[0],fichier))
                    )
                for fichier in sorted(d[2])),
            )
        for d in sorted(dossiers) if len(d[2])]
        )
    l.log(structure)
    return structure

@s.page
def editer(parametres):
    if 'fichier' in parametres:
        with open(os.path.join(c.DATA,EXT,parametres['fichier'])) as f:
            texte = f.read(-1)
    else:
        with open(os.path.join(DOSSIER,'piece.gabc')) as f:
            texte = f.read(-1)
    with open(os.path.join(DOSSIER,'editeur.html')) as f:
        return Template(f.read(-1)).substitute(
                nom = NOM,
                texte = texte,
                )

def traiter(parametres):
    return eval(parametres['action'])(parametres)

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
