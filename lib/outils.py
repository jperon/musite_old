import os
from string import Template
import config as c, auth as a

def page(fonction):
    def afficher(*arguments,**parametres):
        with open(os.path.join('modeles','page.html')) as f: page = Template(f.read(-1))
        index = ('<b>Pages</b><ul>\n'
            + '\n'.join(['<li plain=true><a href=/{0}/>{0}</a></li>'.format(plugin) for plugin in c.PLUGINS])
            + '\n</ul>'
            + admin('<b><a href="/admin/">Admin</a></b><ul>\n'
                    + '<a href="/admin/utilisateurs">utilisateurs</a></ul>\n'
                    )
            + nonauthentifie('''<i><a href="/authentification/">Accès<br>réservé</a></i>'''
                    )
            )
        return page.substitute(
                    titre = c.TITRE,
                    index = index,
                    corps = fonction(*arguments,**parametres),
                    )
    return afficher

@a.seulement(groupe='admin')
def admin(contenu):
    return contenu

@a.masquer(utilisateurs=a.utilisateurs())
def nonauthentifie(contenu):
    return contenu
