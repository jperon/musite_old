#!/usr/bin/env python3
import os,sys,re
from string import Template
sys.path.insert(0, './lib')
sys.path.insert(0, './lib/plugins')
import config
import cherrypy

PLUGINS = {}
for m in config.PLUGINS: PLUGINS[m] = __import__(m)

PWD = os.path.abspath(os.getcwd())

class Site:
    @cherrypy.expose
    def index(self):
        return Page("Coucou !").contenu
    @cherrypy.expose
    def css(self):
        with open(os.path.join('modeles','style.css')) as f: css = Template(f.read(-1))
        try:
            plugin = PLUGINS[cherrypy.session['module']].CSS
        except KeyError:
            plugin = ''
        return css.substitute(plugin = plugin)

class Site_old:
    exposed = True
    @cherrypy.tools.accept(media='text/html')
    @cherrypy.expose
    def GET(self,url='gregorio'):
        if url in MODULES:
            cherrypy.session['module'] = url
            page = Page(PLUGINS[cherrypy.session['plugin']].ACCUEIL)
            return page.contenu
        elif url == 'css': return self.css
        else: return Page('<p>404 : Il doit y avoir une erreur dans votre adresse…</p>').contenu
    @cherrypy.expose
    def POST(self,url='gregorio',texte=''):
        sortie = PLUGINS[cherrypy.session['plugin']].traiter(texte)
        os.renames(os.path.join(sortie['dossier'],sortie['fichier']),os.path.join('static','files',cherrypy.session['plugin'],sortie['fichier']))
        return Page(
            '<object type="application/pdf" data="/static/files/{0}/{1}" zoom="page" width="100%" height="100%"></object>'.format(
                cherrypy.session['plugin'],sortie['fichier']
                )
            ).contenu
    @property
    def css(self):
        with open(os.path.join('modeles','style.css')) as f: css = Template(f.read(-1))
        try:
            plugin = PLUGINS[cherrypy.session['plugin']].CSS
        except KeyError:
            plugin = ''
        return css.substitute(plugin = plugin)

def presenter(accueillir):
    return accueillir

def test():
    return "Coucou !"

class Page:
    def __init__(self,corps):
        with open(os.path.join('modeles','page.html')) as f: self.page = Template(f.read(-1))
        self.index = '<ul>\n' + '\n'.join(['<li plain=true><a href=/{0}>{0}</a></li>'.format(plugin) for plugin in config.PLUGINS]) + '\n</ul>'
        self.corps = corps
    @property
    def contenu(self):
        return self.page.substitute(
                            titre = config.TITRE,
                            index = self.index,
                            corps = self.corps,
                            )


if __name__ == '__main__':
    server_config={
        'server.socket_host': '0.0.0.0',
        'server.socket_port':2443,

        'server.ssl_module':'builtin',
        'server.ssl_certificate':'/etc/ssl/musite.pem',
        'server.ssl_private_key':'/etc/ssl/musite.pem',
        }

    site_config = {
         '/': {
             'tools.sessions.on': True,
             'tools.staticdir.root': PWD
         },
         '/static': {
             'tools.staticdir.on': True,
             'tools.staticdir.dir': './static'
         },
        }
    
    site = Site()
    setattr(site,'test',cherrypy.expose(presenter(test)))
    for m in PLUGINS.keys():
        setattr(site,m,cherrypy.expose(presenter(PLUGINS[m].accueillir)))
    
#    cherrypy.config.update(server_config)
    cherrypy.quickstart(site, '/', site_config)
