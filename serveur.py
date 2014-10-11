#!/usr/bin/env python3
import os,sys,re,hashlib
from string import Template
sys.path.insert(0, './etc')
sys.path.insert(0, './lib')
sys.path.insert(0, './lib/plugins')
import cherrypy
import config
import utilisateurs as u, groupes as g, auth as a, outils as s

PLUGINS = {}
for m in config.PLUGINS: PLUGINS[m] = __import__(m)

PWD = os.path.abspath(os.getcwd())

def presenter(accueillir,plugin):
    def retour(*arguments,**parametres):
        cherrypy.session['plugin'] = plugin
        return str(s.Page(accueillir(*arguments,**parametres)))
    return retour

def utilisateurs():
    return u.lister(os.path.join(PWD,'etc','utilisateurs'))

@property
def groupes():
    return g.lister(os.path.join(PWD,'etc','groupes'))

def crypter_pw(pw):
    pw = pw.encode('utf-8')
    return hashlib.sha1(pw).hexdigest()

class Site:
    @cherrypy.expose
    def index(self):
        with open('lib/index.html','r') as f:
            return s.Page(f.read(-1)).contenu
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
        return str(s.Page('Bonjour, {0} !'.format(cherrypy.request.login)))
    @cherrypy.expose
    @a.reserver(utilisateur='admin')
    def utilisateurs(self):
        return str(s.Page('<br>'.join([u for u in utilisateurs().keys()])))

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
