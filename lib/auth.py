import os,hashlib
import cherrypy as cp
import outils as s, utilisateurs as u, groupes as g

PWD = os.path.abspath(os.getcwd())

def crypter(mdp):
    '''Encodage des mots de passe.'''
    mdp = mdp.encode('utf-8')
    return hashlib.sha1(mdp).hexdigest()

def utilisateurs():
    '''Liste des utilisateurs'''
    return u.lister(os.path.join(PWD,'etc','utilisateurs'))

def groupes():
    '''Liste des groupes.'''
    return g.lister(os.path.join(PWD,'etc','groupes'))

def authentifier(royaume,nom,mdp):
    try:
        return utilisateurs()[nom] == crypter(mdp)
    except KeyError:
        return False

def reserver(**critere):
    def decorateur(fonction):
        def reclamer_authentification(forcer=False):
            if cp.request.login == None:
                try:
                    cp.lib.auth_basic.basic_auth('Accès réservé',authentifier)
                except cp.HTTPError:
                    raise cp.HTTPRedirect('/')
                with open('log','a') as f:
                    f.write(cp.request.login + '\n')
        if 'utilisateur' in critere:
            def afficher(arg):
                reclamer_authentification()
                if cp.request.login in critere['utilisateur']:
                    return fonction(arg)
                else:return '''Accès interdit : seul l'utilisateur {} est admis ici.'''.format(critere['utilisateur'])
        elif 'utilisateurs' in critere:
            def afficher(arg):
                reclamer_authentification()
                if cp.request.login in critere['utilisateurs']:
                    return fonction(arg)
                else:return '''Accès interdit : seuls les utilisateurs {} sont admis ici.'''.format(critere['utilisateurs'])
        elif 'groupe' in critere:
            def afficher(arg):
                reclamer_authentification()
                if cp.request.login in groupes()[critere['groupe']]:
                    return fonction(arg)
                else:return '''Accès interdit : seuls les membres du groupe {} sont admis ici.'''.format(critere['groupe'])
        return afficher
    return decorateur
