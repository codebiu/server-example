import platform
from enum import Enum

class PlatformId(str, Enum):
    """
    platforms
    """
    WIN_x86 = "win-x86"
    WIN_x64 = "win-x64"
    WIN_arm64 = "win-arm64"
    OSX = "osx"
    OSX_x64 = "osx-x64"
    OSX_arm64 = "osx-arm64"
    LINUX_x86 = "linux-x86"
    LINUX_x64 = "linux-x64"
    LINUX_arm64 = "linux-arm64"
    LINUX_MUSL_x64 = "linux-musl-x64"
    LINUX_MUSL_arm64 = "linux-musl-arm64"


class PlatformUtils:
    """
    This class provides utilities for platform detection and identification.
    """

    @staticmethod
    def get_platform_id() -> PlatformId:
        """
        Returns the platform id for the current system
        """
        system = platform.system()
        machine = platform.machine()
        bitness = platform.architecture()[0]
        system_map = {"Windows": "win", "Darwin": "osx", "Linux": "linux"}
        machine_map = {"AMD64": "x64", "x86_64": "x64", "i386": "x86", "i686": "x86", "aarch64": "arm64", "arm64": "arm64"}
        if system in system_map and machine in machine_map:
            platform_id = system_map[system] + "-" + machine_map[machine]
            if system == "Linux" and bitness == "64bit":
                libc = platform.libc_ver()[0]
                if libc != 'glibc':
                    platform_id += "-" + libc
            return PlatformId(platform_id)
        else:
            raise Exception("Unknown platform: " + system + " " + machine + " " + bitness)