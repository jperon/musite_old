import cherrypy
import outils as s

def reserver(**critere):
    def decorateur(fonction):
        if 'utilisateur' in critere:
            def afficher(arg):
                if cherrypy.request.login in critere['utilisateur']:
                    return fonction(arg)
                else:return str(s.Page('''Accès interdit : seul l'utilisateur {} est admis ici.'''.format(critere['utilisateur'])))
        elif 'utilisateurs' in critere:
            def afficher(arg):
                if cherrypy.request.login in critere['utilisateurs']:
                    return fonction(arg)
                else:return str(s.Page('''Accès interdit : seuls les utilisateurs {} sont admis ici.'''.format(critere['utilisateurs'])))
        elif 'groupe' in critere:
            def afficher(arg):
                if cherrypy.request.login in g.lister(os.path.join(PWD,'etc','groupes'))[critere['groupe']]:
                    return fonction(arg)
                else:return str(s.Page('Accès interdit : seuls les membres du groupe {} sont admis ici.'.format(critere['groupe'])))
        return afficher
    return decorateur
