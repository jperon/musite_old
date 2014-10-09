import os,shutil
import subprocess as sp
import cherrypy

PWD = os.path.abspath(os.getcwd())

ACCUEIL = '''
<div id="zonesaisie">
    <form method="post" action="">
        <textarea name="texte" id="saisie"></textarea>
        <br>
        <button type="submit">OK !</button>
    </form>
</div>
<div id="apercu">
    <object type="image/x.djvu" data="/static/gregorio/LU/LU.djvu" zoom="page" width="100%" height="100%">
    Vous semblez n'avoir pas le plugin djvu.
    </object>
</div>
'''

CSS = '''
#zonesaisie {
font-size: 108%;
min-width:48%;
width:auto;
height:100%;
float:left;
}

#apercu {
font-size: 108%;
min-width: 48%;
height:100%;
float:right;
}
'''

def accueillir():
    return ACCUEIL

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
