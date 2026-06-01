import nuke 

menu_item = nuke.menu('Nodes').findItem('Other')
menu_item.addCommand('AOVContactsheet', 'nuke.createNode("AOV_Contactsheet")')