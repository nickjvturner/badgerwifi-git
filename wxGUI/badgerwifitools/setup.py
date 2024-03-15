from setuptools import setup, find_packages

setup(
    name='BadgerWiFi-tools',
    version='0.1.0',
    author='Nick Turner',
    author_email='nick@badgerwifi.co.uk',
    description='A collection of scripts for automating various reporting tasks',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='http://badgerwifi.co.uk',
    packages=find_packages(),
    package_data={'': ['*.txt', '*.md']},  # Include non-Python files if needed
    install_requires=[
        'wxPython>=4.1.1',
        'openpyxl>=3.1.2',
        'pandas>=2.2.0',
        'xlsxwriter>=3.1.9',
        'inflect>=7.0.0',
        'python-docx>=1.1.0',
        'docx2pdf>=0.1.8',
        'pillow>=10.2.0',
        'matplotlib>=3.8.3',
    ],
    classifiers=[
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.9',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
    ],
    python_requires='>=3.9',
    entry_points={
        'console_scripts': [
            'badgerwifitools=badgerwifitools.launcher:main',
        ],
    },
)
