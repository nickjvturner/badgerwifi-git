from setuptools import setup, find_packages

setup(
    name='BadgerWiFi-tools',
    version='0.1.0',
    author='Nick Turner',
    author_email='nick@badgerwifi.co.uk',
    description='A brief description of your app',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='http://badgerwifi.co.uk',
    packages=find_packages(),
    package_data={'': ['*.txt', '*.md']},  # Include non-Python files if needed
    install_requires=[
        'wxPython>=4.1.1',
        'openpyxl>=3.1.2',
        'pandas>=2.2.0',
        'xlsxwriter>=3.1.9'

        # Add other dependencies as needed
    ],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: MIT License',  # Specify your project's license
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.9',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
    ],
    python_requires='>=3.9',
    entry_points={
        'console_scripts': [
            'badgerwifi-tools=your_package_name.your_main_script:main_function',
        ],
    },
)
