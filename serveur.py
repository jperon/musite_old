#!/usr/bin/env python3
import os,sys,re
from string import Template
sys.path.insert(0, './etc')
sys.path.insert(0, './lib')
sys.path.insert(0, './lib/plugins')
import cherrypy as cp
import config as c
import auth as a, outils as s,utilisateurs as u

PLUGINS = {}
for m in c.PLUGINS: PLUGINS[m] = __import__(m)

def presenter(retourner,plugin):
    '''Chargement des plugins.'''
    @cp.expose
    def retour(*arguments,**parametres):
        cp.session['plugin'] = plugin
        return retourner(*arguments,**parametres)
    return retour

class Site:
    '''Cœur du site : chaque méthode décorée par cherrypy.expose
    correspond à une page du site.'''
    @cp.expose
    @s.page
    def index(self):
        '''Page d'accueil.'''
        with open('lib/index.html','r') as f:
            return f.read(-1)
    @cp.expose
    @s.page
    @a.reserver(utilisateurs=a.utilisateurs())
    def authentification(self):
        '''Page sans grand intérêt, si ce n'est de forcer l'authentification
        des utilisateurs.'''
        return 'Bonjour, {0} !'.format(cp.request.login)
    @cp.expose
    def css(self):
        '''Feuille de styles.'''
        with open(os.path.join('modeles','style.css')) as f: css = Template(f.read(-1))
        try:
            plugin = PLUGINS[cp.session['plugin']].css()
        except (AttributeError,KeyError):
            plugin = ''
        return css.substitute(plugin = plugin)

class Admin():
    @cp.expose
    @s.page
    @a.reserver(groupe='admin')
    def index(self):
        return 'Bonjour, {0} !'.format(cp.request.login)
    @cp.expose
    @s.page
    @a.reserver(groupe='admin')
    def utilisateurs(self,**parametres):
        utilisateurs = '''<b>Utilisateurs :</b>\n<table>{liste}</table>
            <br>
            <form method="post" action="/admin/creerutilisateur/">
                <input name="nom" placeholder="Nom"></input>
                <br>
                <input name="mdp" type="password" placeholder="MdP"></input>
                <br>
                <input name="mdp_v" type="password" placeholder="MdP (de nouveau)"></input>
                <br>
                {texte}
                <br>
                <button type="submit">Créer / modifier</button>
            </form>
            '''.format(
                liste = '\n'.join(
                ['<tr><td>{0}&nbsp&nbsp&nbsp</td><td><small><a href=/admin/supprimerutilisateur/?nom={0}>supprimer</a></small></td></tr>'.format(u)\
                        for u in sorted(a.utilisateurs().keys())]
                ),
                texte = parametres['texte'] if 'texte' in parametres else ''
            )
        with open(os.path.join('etc','groupes'),'r') as f:
            groupes = '''
            <script language="javascript" type="text/javascript" src="/public/js/edit_area/edit_area_full.js"></script>
            <script language="javascript" type="text/javascript">
                editAreaLoader.init({{
                    id : "groupes"
                    ,language: "fr"
                    ,word_wrap:false
                    ,show_line_colors:false
                    ,start_highlight: false
                }});
            </script>
            <b>Groupes :</b>\n<br><br>\n
            <form method="post" action="/admin/enregistrergroupes/">
                <textarea name="texte" id="groupes" cols="40" rows="10">{}</textarea>
                <br>
                <button type="submit">Enregistrer</button>
            </form>
            '''.format(f.read(-1))
        return '{}<br>{}'.format(utilisateurs,groupes)
    @cp.expose
    @a.reserver(groupe='admin')
    def creerutilisateur(self,nom,mdp,mdp_v):
        if mdp == mdp_v:
            utilisateur = u.Utilisateur(nom,mdp)
            try:
                utilisateur.ajouter(os.path.join('etc','utilisateurs'))
            except u.UtilisateurExistant:
                utilisateur.modifier(os.path.join('etc','utilisateurs'))
            raise(cp.HTTPRedirect('/admin/utilisateurs/'))
        else:
            return(self.utilisateurs(texte = 'Les mots de passe ne correspondent pas.'))
    @cp.expose
    @a.reserver(groupe='admin')
    def enregistrergroupes(self,texte):
        with open(os.path.join('etc','groupes'),'w') as f:
            f.write(texte)
        raise(cp.HTTPRedirect('/admin/utilisateurs/'))
    @cp.expose
    @a.reserver(groupe='admin')
    def supprimerutilisateur(self,nom):
        u.Utilisateur(nom).supprimer(os.path.join('etc','utilisateurs'))
        raise(cp.HTTPRedirect('/admin/utilisateurs/'))

if __name__ == '__main__':
    site_config = {
         '/': {
             'tools.sessions.on': True,
             'tools.staticdir.root': c.PWD
             },
         '/public': {
             'tools.staticdir.on': True,
             'tools.staticdir.dir': './public'
             },
        }

    site = Site()
    for m in PLUGINS.keys():
        site_config[m] = {'tools.sessions.on':True}
        setattr(site,m,presenter(PLUGINS[m].retourner,m))
    site.admin = Admin()

    @s.page
    def erreur_401(status, message, traceback, version):
        return 'Accès réservé'
    cp.config.update({'error_page.401': erreur_401})
    cp.config.update(c.SERVER_CONFIG)
    cp.quickstart(site, '/', site_config)
