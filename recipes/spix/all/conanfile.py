from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.files import apply_conandata_patches, export_conandata_patches, get, copy, rm, rmdir
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
import os


required_conan_version = ">=1.52.0"


class SpixConan(ConanFile):
    name = "spix"
    description = "UI test automation library for QtQuick/QML Apps"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/faaxm/spix"
    topics = ("automation", "qt", "qml", "qt-quick", "qt5", "qtquick", "automated-testing", "qt-qml", "qml-applications")
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "qt_major": [5, 6],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "qt_major": 6,
    }

    @property
    def _minimum_cpp_standard(self):
        return 14

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("anyrpc/1.0.2")
        if self.options.qt_major == 5:
            self.requires("qt/5.15.6")
        else:
            self.requires("qt/6.3.1")

    def validate(self):
        if self.info.settings.compiler.cppstd:
            check_min_cppstd(self, self._minimum_cpp_standard)
        
    def configure(self):
        # shadertools and qtdeclarative provide the Quick module
        if self.options.qt_major == 6:
            self.options["qt"].qtshadertools = True
        self.options["qt"].qtdeclarative = True
        self.options["qt"].gui = True

    def source(self):
        get(self, **self.conan_data["sources"][self.version], destination=self.source_folder, strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["SPIX_BUILD_EXAMPLES"] = False
        tc.variables["SPIX_BUILD_TESTS"] = False
        tc.variables["SPIX_QT_MAJOR"] = self.options.qt_major
        tc.generate()

        deps = CMakeDeps(self)
        deps.generate()

    def _patch_sources(self):
        apply_conandata_patches(self)

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, pattern="LICENSE.txt", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        cmake = CMake(self)
        cmake.install()

        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "share"))
        rm(self, "*.la", os.path.join(self.package_folder, "lib"))
        rm(self, "*.pdb", os.path.join(self.package_folder, "lib"))
        rm(self, "*.pdb", os.path.join(self.package_folder, "bin"))

    def package_info(self):
        self.cpp_info.libs = ["spix"]
