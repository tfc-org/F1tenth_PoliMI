from glob import glob
import os

from setuptools import find_packages, setup

package_name = 'polimi_reactive'

setup(
    name=package_name,
    version='0.1.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.launch.py')),
        (os.path.join('share', package_name, 'config'), glob('config/*.yaml')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='TF-Costantini',
    maintainer_email='tommasofabrizio.costantini@mail.polimi.it',
    description='Reactive controllers for the PoliMI F1TENTH car: Follow the Gap (/scan -> /drive).',
    license='MIT',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'gap_follow = polimi_reactive.gap_follow_node:main',
        ],
    },
)
