from setuptools import setup

setup(
    name='opencna',
    version='0.1',
    description='Collect, Normalize and Analyze rastrea2r endpoint snapshots',
    long_description=open('README.md').read(),
    license='MIT',
    packages=['cli'],
    zip_safe=False,
    entry_points={
        'console_scripts': [
            'opencna = cli.opencna:main'
        ]
    },
    install_requires=[
        'docker==2.6.1'
    ],
    package_data={
        "precogs": [
            "process/resources/process-schema.json"
        ],
    },
    python_requires='>=2.6, <3'
)
