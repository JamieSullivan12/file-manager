from setuptools import setup

class CONFIG:
    VERSION = 'v1.0-beta2'
    platform = 'darwin-x86_64'
    APP_NAME = f'Exam Document Manager {VERSION}'
    APP = ['main.py']
    DATA_FILES = [
        'theme.json', 
        ('courses', ['courses/COURSE_AL.json','courses/COURSE_IB.json']),
    ]

    OPTIONS = {
        'argv_emulation': False,
        'iconfile': 'EDMico.ico',
        'includes':['dateparser'],
    }

def main():
    setup(
        name=CONFIG.APP_NAME,
        app=CONFIG.APP,
        data_files=CONFIG.DATA_FILES,
        options={'py2app': CONFIG.OPTIONS},
        setup_requires=['py2app'],
        maintainer='foo bar',
        author_email='foo@domain.com',
    )

if __name__ == '__main__':
    main()
