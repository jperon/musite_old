#!/usr/bin/env python3
import os,sys,re,hashlib
from string import Template
sys.path.insert(0, './etc')
sys.path.insert(0, './lib')
sys.path.insert(0, './lib/plugins')
import config
import cherrypy
import utilisateurs as u, groupes as g

PLUGINS = {}
for m in config.PLUGINS: PLUGINS[m] = __import__(m)

PWD = os.path.abspath(os.getcwd())

def presenter(accueillir,plugin):
    def retour(*arguments,**parametres):
        cherrypy.session['plugin'] = plugin
        return str(Page(accueillir(*arguments,**parametres)))
    return retour

def test(arg):
    return 'Coucou'

def reserver(**critere):
    def decorateur(fonction):
        if 'utilisateur' in critere:
            def afficher(arg):
                if cherrypy.request.login in critere['utilisateur']:
                    return fonction(arg)
                else:return str(Page('''Accès interdit : seul l'utilisateur {} est admis ici.'''.format(critere['utilisateur'])))
        elif 'utilisateurs' in critere:
            def afficher(arg):
                if cherrypy.request.login in critere['utilisateurs']:
                    return fonction(arg)
                else:return str(Page('''Accès interdit : seuls les utilisateurs {} sont admis ici.'''.format(critere['utilisateurs'])))
        elif 'groupe' in critere:
            def afficher(arg):
                if cherrypy.request.login in g.lister(os.path.join(PWD,'etc','groupes'))[critere['groupe']]:
                    return fonction(arg)
                else:return str(Page('Accès interdit : seuls les membres du groupe {} sont admis ici.'.format(critere['groupe'])))
        return afficher
    return decorateur

def utilisateurs():
    return u.lister(os.path.join(PWD,'etc','utilisateurs'))

def groupes():
    return g.lister(os.path.join(PWD,'etc','groupes'))

def crypter_pw(pw):
    pw = pw.encode('utf-8')
    return hashlib.sha1(pw).hexdigest()

class Site:
    @cherrypy.expose
    def index(self):
        with open('lib/index.html','r') as f:
            return Page(f.read(-1)).contenu
    @cherrypy.expose
    def css(self):
        with open(os.path.join('modeles','style.css')) as f: css = Template(f.read(-1))
        try:
            plugin = PLUGINS[cherrypy.session['plugin']].CSS
        except (AttributeError,KeyError):
            plugin = ''
        return css.substitute(plugin = plugin)

class Admin():
    @cherrypy.expose
    def index(self):
        return str(Page('Bonjour, {0} !'.format(cherrypy.request.login)))
    @cherrypy.expose
    @reserver(utilisateur='admin')
    def utilisateurs(self):
        return str(Page('<br>'.join([u for u in utilisateurs().keys()])))

class Page:
    def __init__(self,corps):
        with open(os.path.join('modeles','page.html')) as f: self.page = Template(f.read(-1))
        self.index = ('<b>Pages</b><ul>\n'
            + '\n'.join(['<li plain=true><a href=/{0}/>{0}</a></li>'.format(plugin) for plugin in config.PLUGINS])
            + '\n</ul>'
            + '<b><a href="/admin/">Admin</a></b><ul>\n'
            + '<a href="/admin/utilisateurs">utilisateurs</a></ul>\n'
            )
        self.corps = corps
    @property
    def contenu(self):
        return self.page.substitute(
                            titre = config.TITRE,
                            index = self.index,
                            corps = self.corps,
                            )
    def __str__(self):
        return self.contenu

if __name__ == '__main__':
    config.SERVER_CONFIG

    site_config = {
         '/': {
             'tools.sessions.on': True,
             'tools.staticdir.root': PWD
             },
         '/static': {
             'tools.staticdir.on': True,
             'tools.staticdir.dir': './static'
             },
         '/admin': {
             'tools.basic_auth.on': True,
             'tools.basic_auth.realm': 'Accès réservé',
             'tools.basic_auth.users': utilisateurs,
             'tools.basic_auth.encrypt': crypter_pw
             }
        }

    site = Site()
    for m in PLUGINS.keys():
        site_config[m] = {'tools.sessions.on':True}
        setattr(site,m,cherrypy.expose(presenter(PLUGINS[m].accueillir,m)))
    site.admin = Admin()

    cherrypy.config.update(config.SERVER_CONFIG)
    cherrypy.quickstart(site, '/', site_config)
