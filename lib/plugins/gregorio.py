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

def titregabc(f):
        try:
            entetes = g.Gabc(g.FichierTexte(f).contenu).entetes
        except UnicodeDecodeError: return '''<b><i>Erreur d'encodage : {}</i></b>'''.format(f)
        if 'name' in entetes: return entetes['name']
        else: return '<b><i>À corriger : fichier sans balise "name" : {}</i></b>'.format(f)

@s.page
def accueillir():
    racine = os.path.join(c.DATA,EXT)
    dossiers = os.walk(racine)
    structure = '\n'.join(
        ['<b>{0}</b>\n<ul id="listechants">\n\t<li>{1}</li>\n</ul>'.format(
            dossier.replace(racine + os.sep,'').capitalize(),
            '</li>\n\t<li>'.join(
                '<a href="/gregorio/afficher/?fichier={0}">{1}</a>'.format(
                    os.path.join(dossier.replace(racine + os.sep,''),fichier),
                    titregabc(os.path.join(dossier,fichier))
                    )
                for fichier in sorted(fichiers)),
            )
        for dossier, sousdossiers, fichiers in sorted(dossiers) if len(fichiers)]
        )
    return structure

@s.page
def afficher(parametres):
    fichier = parametres['fichier'].split('/')
    sousdossier,fichierpdf = fichier[:-1],fichier[-1].replace('.gabc','.pdf')
    dossier = os.path.join(c.DATA,'pdf',os.sep.join(sousdossier))
    if not os.path.isfile(os.path.join(dossier,fichierpdf)):
        parametres['papier'] = 'a6paper'
        parametres['taillepolice'] = '12'
        parametres['marge'] = '20px'
        compiler(parametres,dossier,fichierpdf)
    with open(os.path.join(DOSSIER,'apercu.html')) as f:
        return Template(f.read(-1)).substitute(
                titre = titregabc(os.path.join(c.DATA,'gabc',os.sep.join(fichier))),
                corps = '<object type="application/pdf" data="/public/data/pdf/{0}/{1}" zoom="page" width="100%" height="100%"></object>'.format(
                        '/'.join(sousdossier),fichierpdf
                        ),
                actions = (
                    'Télécharger '
                    + s.authentifie(
                        '<a href=/gregorio/editer/?fichier={}>Éditer</a>'.format(
                            parametres['fichier']
                            )
                        )
                    )
                )

@s.page
def telecharger(parametres):pass
    #compiler()

@s.page
def editer(parametres):
    if 'fichier' in parametres:
        anciennom = parametres['fichier']
        with open(os.path.join(c.DATA,EXT,anciennom)) as f:
            texte = f.read(-1)
    else:
        with open(os.path.join(DOSSIER,'piece.gabc')) as f:
            texte = f.read(-1)
    with open(os.path.join(DOSSIER,'editeur.html')) as f:
        return Template(f.read(-1)).substitute(
                nom = NOM,
                texte = texte,
                anciennom = anciennom if anciennom else '',
                )

def traiter(parametres):
    return eval(parametres['action'])(parametres)

def compiler(parametres,dossier,fichier):
    if 'texte' in parametres.keys(): contenu = parametres['texte']
    elif 'fichier' in parametres:
        with open(os.path.join(c.DATA,'gabc',parametres['fichier'])) as f:
            contenu = f.read(-1)
    if 'papier' not in parametres: parametres['papier'] = 'a5paper'
    if 'taillepolice' not in parametres: parametres['taillepolice'] = '12'
    if 'marge' in parametres: parametres['marge'] = '\\usepackage[margin={0}]{{geometry}}'.format(parametres['marge'])
    else: parametres['marge'] = ''
    gabc = 'partition.gabc'
    commande = ['lualatex','-interaction=batchmode','--shell-escape','partition']
    destination = os.path.join(c.TMP,NOM)
    shutil.rmtree(destination,True)
    shutil.copytree(
        os.path.join('modeles',NOM),
        destination,
        True
        )
    try:
        os.chdir(destination)
        with open(os.path.join('gabc',gabc),'w') as f:
            f.write(contenu)
        with open('Gabarit.tex','r') as g:
            with open('partition.tex','w') as f:
                f.write(
                    Template(g.read(-1)).substitute(
                        papier = parametres['papier'],
                        taillepolice = parametres['taillepolice'],
                        marge = parametres['marge'],
                        )
                    )
        environnement = os.environ.copy()
        environnement['TEXINPUTS'] = 'lib:'
        sortie,erreurs = sp.Popen(commande,env=environnement,stdout=sp.PIPE,stderr=sp.PIPE).communicate()
    finally:
        os.chdir(c.PWD)
    os.renames(os.path.join(destination,'partition.pdf'),os.path.join(dossier,fichier))

def enregistrer(parametres):
    gabc = g.Gabc(parametres['texte'])
    dossier = os.path.join(c.DATA,EXT,gabc.entetes['office-part'])
    os.makedirs(dossier,exist_ok=True)
    fichier = gabc.entetes['name'].replace(' ','_').lower() + '.' + EXT
    emplacement = os.path.join(dossier,fichier)
    with open(emplacement,'w') as f:
        f.write(parametres['texte'])
    try:
        ancienemplacement = parametres['anciennom'].replace('/',os.sep)
        if ancienemplacement != emplacement:
            os.remove(ancienemplacement)
    except KeyError: pass
    raise(cp.HTTPRedirect('/' + NOM))
