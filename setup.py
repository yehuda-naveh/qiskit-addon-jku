# -*- coding: utf-8 -*-

# Copyright 2018 IBM RESEARCH. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# =============================================================================

import sys
import os
import platform
from distutils.command.build import build
from multiprocessing import cpu_count
from subprocess import call

from setuptools import setup, find_packages
from setuptools.dist import Distribution
from setuptools import setup, find_packages

class JKUSimulatorBuild(build):
    def run(self):
        super().run()
        # Store the current working directory, as invoking cmake involves
        # an out of source build and might interfere with the rest of the steps.
        current_directory = os.getcwd()

        try:
            supported_platforms = ['Linux', 'Darwin', 'Windows']
            current_platform = platform.system()
            if current_platform not in supported_platforms:
                # TODO: stdout is silenced by pip if the full setup.py invocation is
                # successful, unless using '-v' - hence the warnings are not printed.
                print('WARNING: JKU simulator is meant to be built with these '
                      'platforms: {}. We will support other platforms soon!'
                      .format(supported_platforms))
                return

            cmd_cmake = ['cmake', '-vvv']
            if 'USER_LIB_PATH' in os.environ:
                cmd_cmake.append('-DUSER_LIB_PATH={}'.format(os.environ['USER_LIB_PATH']))
            if current_platform == 'Windows':
                # We only support MinGW so far
                cmd_cmake.append("-GMinGW Makefiles")
            cmd_cmake.append('.')
            cmd_cmake.append('-Bbuild/lib/qiskit_addon_jku')

            cmd_make = ['make', '-C', 'build/lib/qiskit_addon_jku']

            def compile_simulator():
                call(cmd_cmake)
                call(cmd_make)

            self.execute(compile_simulator, [], 'Compiling JKU Simulator')
        except Exception as e:
            print(str(e))
            print("WARNING: Seems like the JKU simulator can't be built, Qiskit will "
                  "install anyway, but won't have this simulator support.")

        # Restore working directory.
        os.chdir(current_directory)

# This is for creating wheel specific platforms
class BinaryDistribution(Distribution):
    def has_ext_modules(self):
        return True
    
setup(
    name="qiskit_addon_jku",
    version="0.1.0",
    author="QISKit Development Team",
    author_email="qiskit@us.ibm.com",
    description="QISKit simulator whose backend is based on JKU's simulator",
    long_description = "This module contains [QISKit](https://www.qiskit.org/) simulator whose backend is written in JKU's simulator. This simulator simulate a Quantum circuit on a classical computer.",
    url="https://github.com/QISKit/qiskit-addon-jku",
    license="Apache 2.0",
    classifiers=[
        "Environment :: Console",
        "License :: OSI Approved :: Apache Software License",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: MacOS",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Topic :: Scientific/Engineering",
    ],
    install_requires=['qiskit>=0.5'],
    keywords="qiskit quantum jku_simulator",
    packages=find_packages(exclude=['test*']),
    include_package_data=True,
    cmdclass={
        'build': JKUSimulatorBuild,
    },
    distclass=BinaryDistribution
    
)
