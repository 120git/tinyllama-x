import textwrap
import pytest

from tinyllamax.utils.distro import parse_os_release_content, preferred_pkg_manager


@pytest.mark.parametrize(
    "content,expected_id,expected_version,pm",
    [
        (
            textwrap.dedent(
                """
                NAME="Ubuntu"
                VERSION="24.04 LTS (Noble Numbat)"
                ID=ubuntu
                ID_LIKE=debian
                VERSION_ID="24.04"
                """
            ),
            "ubuntu",
            "24.04",
            "apt",
        ),
        (
            textwrap.dedent(
                """
                NAME="Debian GNU/Linux"
                VERSION="12 (bookworm)"
                ID=debian
                VERSION_ID="12"
                """
            ),
            "debian",
            "12",
            "apt",
        ),
        (
            textwrap.dedent(
                """
                NAME=Fedora Linux
                VERSION="40 (Workstation Edition)"
                ID=fedora
                VERSION_ID=40
                """
            ),
            "fedora",
            "40",
            "dnf",
        ),
        (
            textwrap.dedent(
                """
                NAME="Arch Linux"
                ID=arch
                PRETTY_NAME="Arch Linux"
                VERSION_ID=rolling
                """
            ),
            "arch",
            "rolling",
            "pacman",
        ),
        (
            textwrap.dedent(
                """
                NAME="openSUSE Tumbleweed"
                ID="opensuse-tumbleweed"
                ID_LIKE="suse opensuse"
                VERSION_ID="20241104"
                """
            ),
            "opensuse-tumbleweed",
            "20241104",
            "zypper",
        ),
        (
            textwrap.dedent(
                """
                NAME="Alpine Linux"
                ID=alpine
                VERSION_ID=3.19.1
                """
            ),
            "alpine",
            "3.19.1",
            "apk",
        ),
    ],
)
def test_parse_and_pm(content, expected_id, expected_version, pm):
    did, ver = parse_os_release_content(content)
    assert did == expected_id
    assert ver == expected_version
    assert preferred_pkg_manager(did) == pm
