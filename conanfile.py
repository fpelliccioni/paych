#
# Copyright (c) 2017 Bitprim developers (see AUTHORS)
#
# This file is part of Bitprim.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

import os
from conans import ConanFile, CMake
from conans import __version__ as conan_version
from conans.model.version import Version
import importlib


def option_on_off(option):
    return "ON" if option else "OFF"

def get_content(file_name):
    # print(os.path.dirname(os.path.abspath(__file__)))
    # print(os.getcwd())
    # print(file_name)
    file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), file_name)
    with open(file_path, 'r') as f:
        return f.read()

def get_version():
    return get_content('conan_version')

def get_channel():
    return get_content('conan_channel')

def get_conan_req_version():
    return get_content('conan_req_version')

microarchitecture_default = 'x86_64'

def get_cpuid():
    try:
        cpuid = importlib.import_module('cpuid')
        return cpuid
    except ImportError:
        print("*** cpuid could not be imported")
        return None

def get_cpu_microarchitecture_or_default(default):
    cpuid = get_cpuid()
    if cpuid != None:
        return '%s' % (''.join(cpuid.cpu_microarchitecture()))
    else:
        return default

def get_cpu_microarchitecture():
    return get_cpu_microarchitecture_or_default(microarchitecture_default)


class BitprimPaymentChannelConan(ConanFile):
    name = "paych"
    version = get_version()
    license = "http://www.boost.org/users/license.html"
    url = "https://github.com/bitprim/bitprim-payment-channels"
    description = "Payment Channels Experiments"
    settings = "os", "compiler", "build_type", "arch"
    # settings = "os", "arch"

    if conan_version < Version(get_conan_req_version()):
        raise Exception ("Conan version should be greater or equal than %s" % (get_conan_req_version(), ))

    options = {
        "currency": ['BCH', 'BTC', 'LTC'],
        "microarchitecture": "ANY",
        "no_compilation": [True, False],
        "verbose": [True, False],
    }

    default_options = "currency=BCH", \
                      "microarchitecture=_DUMMY_",  \
                      "no_compilation=False",  \
                      "verbose=False"
    
    generators = "cmake"
    exports = "conan_channel", "conan_version", "conan_req_version"
    exports_sources = "CMakeLists.txt", "cmake/*", "src/*", "bitprimbuildinfo.cmake"
    build_policy = "missing"

    def requirements(self):
        if not self.options.no_compilation and self.settings.get_safe("compiler") is not None:
            self.requires("bitprim-node/0.8@bitprim/%s" % get_channel())

    def configure(self):
        if self.options.no_compilation or (self.settings.compiler == None and self.settings.arch == 'x86_64' and self.settings.os in ('Linux', 'Windows', 'Macos')):
            self.settings.remove("compiler")
            self.settings.remove("build_type")

        if self.options.microarchitecture == "_DUMMY_":
            self.options.microarchitecture = get_cpu_microarchitecture()

            if get_cpuid() == None:
                march_from = 'default'
            else:
                march_from = 'taken from cpuid'

        else:
            march_from = 'user defined'
        
        self.options["*"].microarchitecture = self.options.microarchitecture
        self.output.info("Compiling for microarchitecture (%s): %s" % (march_from, self.options.microarchitecture))

        self.options["*"].currency = self.options.currency
        self.output.info("Compiling for currency: %s" % (self.options.currency,))


    def package_id(self):
        self.info.requires.clear()
        self.info.settings.compiler = "ANY"
        self.info.settings.build_type = "ANY"
        self.info.options.no_compilation = "ANY"
        self.info.options.verbose = "ANY"

        
        

    def deploy(self):
        self.copy("bn.exe", src="bin")     # copy from current package
        self.copy("bn", src="bin")         # copy from current package
        # self.copy_deps("*.dll") # copy from dependencies        


    def build(self):
        cmake = CMake(self)
        
        cmake.definitions["USE_CONAN"] = option_on_off(True)
        cmake.definitions["NO_CONAN_AT_ALL"] = option_on_off(False)
        cmake.verbose = self.options.verbose
        cmake.definitions["CURRENCY"] = self.options.currency
        cmake.definitions["MICROARCHITECTURE"] = self.options.microarchitecture

        if self.settings.compiler == "gcc":
            if float(str(self.settings.compiler.version)) >= 5:
                cmake.definitions["NOT_USE_CPP11_ABI"] = option_on_off(False)
            else:
                cmake.definitions["NOT_USE_CPP11_ABI"] = option_on_off(True)
        elif self.settings.compiler == "clang":
            if str(self.settings.compiler.libcxx) == "libstdc++" or str(self.settings.compiler.libcxx) == "libstdc++11":
                cmake.definitions["NOT_USE_CPP11_ABI"] = option_on_off(False)

        cmake.definitions["BITPRIM_BUILD_NUMBER"] = os.getenv('BITPRIM_BUILD_NUMBER', '-')
        cmake.configure(source_dir=self.source_folder)
        cmake.build()

    # def imports(self):
    #     self.copy("*.h", "", "include")

    def package(self):
        self.copy("pctest.exe", dst="bin", src="bin") # Windows
        self.copy("pctest", dst="bin", src="bin") # Linux / Macos

