'''
Plugin servant à traiter les partitions grégoriennes.
'''
import os
import shutil
import subprocess as sp
import traceback as tb
import ast
from string import Template
import config as c
import jrnl as l
import outils as s
import auth as a
import gabctk as g
import cherrypy as cp

NOM = 'gregorio'
EXT = 'gabc'
DOSSIER = os.path.join('lib', 'plugins', 'gregorio')


def css():
    '''Styles de page'''
    with open(os.path.join(DOSSIER, 'style.css')) as fichier:
        return fichier.read(-1)


def retourner(*arguments, **parametres):
    '''Fonction maîtresse, pilotant le reste en fonction des arguments.'''
    l.log(
        'arguments : {}\n paramètres : {}\n'.format(
            str(arguments),
            str(parametres)
            )
        )
    try:
        return eval(arguments[0])(parametres)
    except (KeyError, IndexError):
        return accueillir()


def titregabc(fichier):
    '''Titre de la partition.'''
    try:
        entetes = g.Gabc(g.FichierTexte(fichier).contenu).entetes
    except UnicodeDecodeError:
        return '''<b><i>Erreur d'encodage : {}</i></b>'''.format(fichier)
    if 'name' in entetes:
        return entetes['name']
    else:
        return (
            '<b><i>'
            + 'À corriger : fichier sans balise "name" : {}'
            + '</i></b>'
            ).format(fichier)


@s.page
def accueillir():
    '''Page d'accueil, listant les fichiers gabc.'''
    racine = os.path.join(c.DATA, EXT)
    dossiers = os.walk(racine)
    page = (
        s.authentifie(
            '<div id="actions">'
            + '<a href="/gregorio/creer/">Créer une nouvelle pièce</a>\n<br>\n'
            + '</div>'
            )
        + '\n'.join(
            [
                (
                    '<b>{0}</b>\n<ul id="listechants">\n'
                    + '\t<li>{1}</li>\n</ul>'
                ).format(
                    dossier.replace(racine + os.sep, '').capitalize(),
                    '</li>\n\t<li>'.join(
                        (
                            '<a href="/gregorio/afficher/?fichier={0}">{1}</a>'
                        ).format(
                            os.path.join(
                                dossier.replace(racine + os.sep, ''),
                                fichier
                                ),
                            titregabc(os.path.join(dossier, fichier))
                            )
                        for fichier in sorted(
                            fichiers,
                            key=lambda x: x.lower()
                            )
                        ),
                )
                for dossier, sousdossiers, fichiers
                in sorted(dossiers) if len(fichiers)
            ]
            )
        )
    return page


@s.page
def afficher(parametres):
    '''Aperçu d'une partition, avec en parallèle le Liber Usualis.'''
    chemin = parametres['fichier'].split('/')
    sousdossier = chemin[:-1]
    fichierpdf = chemin[-1].replace('.gabc', '.pdf')
    dossier = os.path.join(c.DATA, 'pdf', os.sep.join(sousdossier))
    if not os.path.isfile(os.path.join(dossier, fichierpdf)):
        parametres['papier'] = 'a6paper'
        parametres['taillepolice'] = '12'
        parametres['marge'] = '20px'
        compiler(parametres, dossier, fichierpdf)
    with open(os.path.join(DOSSIER, 'apercu.html')) as fichier:
        return Template(fichier.read(-1)).substitute(
            titre=titregabc(
                os.path.join(c.DATA, 'gabc', os.sep.join(chemin))
                ),
            corps=(
                '<object type="application/pdf" '
                + 'data="/public/data/pdf/{0}/{1}" '
                + 'zoom="page" width="100%" height="100%">'
                + '</object>'
                ).format(
                    '/'.join(sousdossier), fichierpdf
                    ),
            actions=(
                'Mettre en page'
                + s.authentifie(
                    (
                        ' − '
                        + '<a href=/gregorio/editer/?fichier={}>Éditer</a>'
                    ).format(
                        parametres['fichier']
                        )
                    )
                )
            )


@s.page
def creer(parametres):
    '''Création d'une nouvelle partition.'''
    with open(os.path.join(DOSSIER, 'creation.html')) as fichier:
        return Template(fichier.read(-1)).substitute(nom=NOM)


@s.page
def editer(parametres):
    '''Édition d'une partition.'''
    if 'fichier' in parametres:
        cp.session['anciennom'] = parametres['fichier']
        with open(
            os.path.join(
                c.DATA, EXT, cp.session['anciennom']
                )
        ) as fichier:
            texte = fichier.read(-1)
    else:
        with open(os.path.join(DOSSIER, 'piece.gabc')) as fichier:
            texte = Template(fichier.read(-1)).substitute(
                titre=parametres['titre'] if parametres['titre'] else 'nom',
                mode=parametres['mode'] if parametres['mode'] else '1.',
                categorie=(
                    parametres['type']
                    if parametres['type']
                    else 'antiphona'
                    ),
                )
    with open(os.path.join(DOSSIER, 'editeur.html')) as fichier:
        return Template(fichier.read(-1)).substitute(
            nom=NOM,
            texte=texte,
            enregistrer=s.authentifie(
                '<button type="submit" name="action" value="enregistrer">'
                + 'Enregistrer</button>'
                )
            )


def traiter(parametres):
    '''Distinction entre la simple mise en page et l'enregistrement
    d'une partition.'''
    return eval(parametres['action'])(parametres)


def compiler(parametres, dossier, fichierpdf):
    '''Compilation d'une partition.'''
    if 'texte' in parametres.keys():
        contenu = parametres['texte']
    elif 'fichier' in parametres:
        with open(
            os.path.join(
                c.DATA, 'gabc', parametres['fichier']
                )
        ) as fichier:
            contenu = fichier.read(-1)
    if 'papier' not in parametres:
        parametres['papier'] = 'a5paper'
    if 'taillepolice' not in parametres:
        parametres['taillepolice'] = '12'
    parametres['marge'] = (
        '\\usepackage[margin={0}]{{geometry}}'.format(parametres['marge'])
        ) if 'marge' in parametres else ''
    gabc = 'partition.gabc'
    commande = [
        'lualatex',
        '-interaction=batchmode',
        '--shell-escape',
        'partition'
        ]
    destination = os.path.join(c.TMP, NOM)
    shutil.rmtree(destination, True)
    shutil.copytree(
        os.path.join('modeles', NOM),
        destination,
        True
        )
    try:
        os.chdir(destination)
        with open(os.path.join('gabc', gabc), 'w') as fichier:
            fichier.write(contenu)
        with open('Gabarit.tex', 'r') as gabarit:
            with open('partition.tex', 'w') as fichier:
                fichier.write(
                    Template(gabarit.read(-1)).substitute(
                        papier=parametres['papier'],
                        taillepolice=parametres['taillepolice'],
                        marge=parametres['marge'],
                        )
                    )
        environnement = os.environ.copy()
        environnement['TEXINPUTS'] = 'lib:'
        sortie, erreurs = sp.Popen(
            commande,
            env=environnement,
            stdout=sp.PIPE,
            stderr=sp.PIPE
            ).communicate()
        l.log(
            'Sortie :\n{}\n\n'.format(sortie)
            + 'Erreurs :\n{}\n\n'.format(erreurs)
            )
    finally:
        os.chdir(c.PWD)
    os.renames(
        os.path.join(destination, 'partition.pdf'),
        os.path.join(dossier, fichierpdf)
        )


def telecharger(parametres):
    '''Téléchargement d'une partition mise en page.'''
    gabc = g.Gabc(parametres['texte'])
    fichierpdf = (
        s.sansaccents(
            gabc.entetes['name'].replace(' ', '_').lower()
            )
        + '.pdf'
        )
    dossier = os.path.join(c.DATA, 'pdf', gabc.entetes['office-part'])
    compiler(parametres, dossier, fichierpdf)
    return cp.lib.static.serve_file(os.path.join(dossier, fichierpdf))


@a.reserver(utilisateurs=a.utilisateurs())
def enregistrer(parametres):
    '''Enregistrement d'une partition.'''
    gabc = g.Gabc(parametres['texte'])
    dossier = os.path.join(c.DATA, EXT, gabc.entetes['office-part'])
    os.makedirs(dossier, exist_ok=True)
    fichiergabc = (
        s.sansaccents(
            gabc.entetes['name'].replace(' ', '_').lower()
            )
        + '.'
        + EXT
        )
    emplacement = os.path.join(dossier, fichiergabc)
    with open(emplacement, 'w') as fichier:
        fichier.write(parametres['texte'])
    try:
        ancienemplacement = os.path.join(
            c.DATA, EXT,
            cp.session['anciennom'].replace('/', os.sep),
            )
        if ancienemplacement != emplacement:
            os.remove(ancienemplacement)
        try:
            os.remove(
                ancienemplacement.replace(
                    '.' + EXT, '.pdf'
                    ).replace(
                        '/' + EXT, '/pdf'
                        )
                )
        except FileNotFoundError:
            pass
    except KeyError:
        pass
    try:
        os.remove(
            emplacement.replace(
                '.' + EXT, '.pdf'
                ).replace(
                    '/' + EXT, '/pdf'
                    )
            )
    except Exception as erreur:
        l.log(erreur)
        tb.format_exc()
    raise cp.HTTPRedirect(
        '/{nom}/afficher/?fichier={fichier}'.format(
            nom=NOM,
            fichier='/'.join((gabc.entetes['office-part'], fichiergabc))
            )
        )
