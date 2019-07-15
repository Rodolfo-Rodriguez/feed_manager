#!/usr/bin/python2

import sys

sys.path.append('/home/ubuntu/develop/radio-v3/app')

from feed_manager import FeedManager

# if len(sys.argv) < 2:
#   print '[ERROR] Uso: {} [url]'.format(sys.argv[0])
#   sys.exit(2)

# url = sys.argv[1]

#url = 'https://espectador.com/otroelefante/maxiguerra/las-vidas-extras-de-wilko-johnson'
#url = 'https://delsol.uy/lamesa/deporgol/ranchero-con-detalles-de-la-gira-de-penarol-en-estados-unidos'
#url = 'https://delsol.uy/notoquennada/ntnconcentrado/miranda-y-la-union-ultraderechista-talvi-y-la-renovacion-cosse-y-su-aporte-en-la-campana'
#url = 'https://delsol.uy/copaamerica/audios/sol_13671'
#url = 'https://delsol.uy/abrancancha/inmemoriam/la-vida-de-alfredo-zitarrosa-el-exilio-y-su-compromiso-con-el-pueblo'
url = 'https://www.oceano.uy/dearribaunrayo/ernesto/18264-ernesto-para-ninos'
url = 'https://www.oceano.uy/todopasa/musica/18290-newman-el-musicalizador-de-disney-pixar'

feed_manager = FeedManager(url)

title = feed_manager.get_title()
#audio_url = feed_manager.get_audio_url()
#pub_date = feed_manager.get_pub_date()
#description = feed_manager.get_description()

print title
#print audio_url
#print pub_date 
#print description
