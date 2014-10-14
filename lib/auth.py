import os,hashlib
import cherrypy as cp
import utilisateurs as u, groupes as g, jrnl as l

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
        if utilisateurs()[nom] == crypter(mdp):
            critere = cp.session['reserve']
            if 'utilisateur' in critere:
                return (nom == critere['utilisateur'])
            elif 'utilisateurs' in critere:
                return (nom in critere['utilisateurs'])
            elif 'groupe' in critere:
                return (nom in groupes()[critere['groupe']])
    except KeyError:
        return False

def reserver(**critere):
    def decorateur(fonction):
        def afficher(arg):
            cp.session['reserve'] = critere
            if cp.lib.auth_basic.basic_auth('Droits insuffisants',authentifier) == None:
                return fonction(arg)
            else:return '''Accès interdit'''
        return afficher
    return decorateur

def seulement(**critere):
    def decorateur(fonction):
        def afficher(arg):
            royaume = 'Droits insuffisants'
            try:
                if cp.lib.auth_basic.basic_auth(royaume,authentifier) == None:
                    return fonction(arg)
                else: return ''
            except cp.HTTPError: return ''
        return afficher
    return decorateur

def exclure(**critere):
    def decorateur(fonction):
        def afficher(arg):
            try:
                if cp.lib.auth_basic.basic_auth('Droits insuffisants',authentifier) == None:
                    return ''
                else: return fonction(arg)
            except cp.HTTPError: return fonction(arg)
        return afficher
    return decorateur
