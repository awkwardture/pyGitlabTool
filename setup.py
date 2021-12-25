from setuptools import setup

setup(
    name='pyGitlabTool',
    version='0.3.0',
    packages=['gitlabtool'],
    install_requires=[
        "requests",
        "jinja2",
        "flask",
        "tornado"
    ],
    entry_points={
        'console_scripts': [
            # name_of_executable = module.with:function_to_execute
            'pyGitlabTool = gitlabtool.__main__:main',
            'gitlog2chglog = gitlabtool.__main__:g2c'
        ]
    },
    # scripts=['bin/pyGitlabTool'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Environment :: Other Environment",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    url='http://github.com/awkwardture/pyGitlabTool',
    license='',
    author='ture',
    author_email='wjj@iantong.net',
    description=''
)
