from setuptools import setup, find_packages

# this is a temporary way to add to the path variable other modules during the runtime
# sys.path.append('./src/view')
# sys.path.append('./src/model')
# sys.path.append('./src/control') 

sys.path.append('./src/view')
sys.path.append('./src/model')
sys.path.append('./src/control') 

def readme():
    with open('readme.txt') as f:
        return f.read()

setup(
    name='house-manager-app',
    version='0.4',
    description='The beta version of the ultimate house manager',
    long_description=readme(),
    url='http://github.com/storborg/funniest',
    author='Zcio developer Team',
    author_email='flyingcircus@example.com',
    license='MIT',
    package_dir={'': './src'},
    packages=find_packages(),
    install_requires=[
        # from installations:
        # from View:
        'PySide',
        'pyqtgraph',
        # from model:
        'mysql-connector',
        # from controller:

    ],
    zip_safe=True,
    include_package_data=True # this cill copy the manifest data to de instalation folder (python site-packages)
)
