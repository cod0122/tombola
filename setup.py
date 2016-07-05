'''
Created on 24/gen/2013

@author: alberto
'''
from cx_Freeze import setup, Executable

executables = [
        Executable("tombolaApp.py", icon="logo_tmb.ico", 
                   targetName = "Tombola.exe",
                   shortcutName = "TmbApp",
                   shortcutDir = "d:\tombola",
                   appendScriptToExe=True,
                   appendScriptToLibrary=False)
]

buildOptions = dict(
        compressed = True,
        includes = ['tombolaApp','tombolaTabellone','tombola','tombolaConfig'],
        create_shared_zip = False)

setup(
        name = "tombola",
        version = "1.0",
        description = 'Gioco della Tombola',
        options = dict(build_exe = buildOptions),
        executables = executables
       ,data_files=[('img', ['img/logo_tmb.png','img/antilope.png'
        ,'img/aquila.png'
        ,'img/cervo.png'
        ,'img/cinciallegra.png'
        ,'img/corvo.png'
        ,'img/fenicottero.png'
        ,'img/gorilla.png'
        ,'img/logo_tmb.png'
        ,'img/lupo.png'
        ,'img/pulcinelladimare.png'
        ,'img/rana.png'
        ,'img/riccio.png'
        ,'img/tartaruga.png'
        ,'img/topo.png'
        ,'img/upupa.png'
        ,'courbd.ttf'
        ,'freesansbold.ttf'
        ])]
        )