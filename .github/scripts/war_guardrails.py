#!/usr/bin/env python3
"""Pre-publish safety checks for the pi-web-tools WAR.

1. Bytecode ceiling: every class under WEB-INF/classes must be Java 8 (major 52)
   or lower. The build JDK is newer than the runtime (Tomcat on Java 8), so a
   dropped `release="8"` in build.xml would otherwise ship classes that crash
   production with UnsupportedClassVersionError.
2. Bundled Oracle driver: ED-21599 requires no duplicate ojdbc*.jar. The driver
   belongs in <tomcat>/lib for the JNDI datasources; a copy in WEB-INF/lib causes
   classloader conflicts. Reported as a warning unless --fail-on-bundled-ojdbc.
3. Sanity: the WAR has a WEB-INF/web.xml and at least one compiled class.

Usage: war_guardrails.py <war> [--max-major 52] [--fail-on-bundled-ojdbc]
"""
import argparse
import struct
import sys
import zipfile

JAVA_VERSION_BY_MAJOR = {50: "6", 51: "7", 52: "8", 53: "9", 54: "10", 55: "11", 61: "17", 65: "21"}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("war")
    parser.add_argument("--max-major", type=int, default=52)
    parser.add_argument("--fail-on-bundled-ojdbc", action="store_true")
    args = parser.parse_args()

    too_new, ojdbc, classes = [], [], 0
    try:
        zf = zipfile.ZipFile(args.war)
    except (OSError, zipfile.BadZipFile) as exc:
        print(f"::error::{args.war} is not a readable WAR: {exc}")
        return 1

    with zf:
        names = zf.namelist()
        for name in names:
            if name.startswith("WEB-INF/classes/") and name.endswith(".class"):
                with zf.open(name) as fh:
                    header = fh.read(8)
                if len(header) == 8 and header[:4] == b"\xca\xfe\xba\xbe":
                    classes += 1
                    major = struct.unpack(">H", header[6:8])[0]
                    if major > args.max_major:
                        too_new.append((name, major))
            base = name.rsplit("/", 1)[-1].lower()
            if name.startswith("WEB-INF/lib/") and base.startswith("ojdbc") and base.endswith(".jar"):
                ojdbc.append(name)

    failed = False
    if "WEB-INF/web.xml" not in names:
        print("::error::WEB-INF/web.xml missing - this does not look like the ADS_web_tools WAR")
        failed = True
    if classes == 0:
        print("::error::no compiled classes found under WEB-INF/classes")
        failed = True
    if too_new:
        failed = True
        limit = JAVA_VERSION_BY_MAJOR.get(args.max_major, args.max_major)
        print(f"::error::{len(too_new)} class(es) compiled for a newer Java than the runtime (Java {limit}) - would crash Tomcat:")
        for name, major in too_new[:20]:
            print(f"  {name}: major {major} (Java {JAVA_VERSION_BY_MAJOR.get(major, '?')})")
    if ojdbc:
        level = "error" if args.fail_on_bundled_ojdbc else "warning"
        print(f"::{level}::Oracle driver bundled in the WAR ({', '.join(ojdbc)}). "
              "ED-21599 requires no duplicate ojdbc*.jar - it should live only in <tomcat>/lib.")
        failed = failed or args.fail_on_bundled_ojdbc

    print(f"Checked {classes} classes; max allowed major version {args.max_major}; bundled ojdbc: {ojdbc or 'none'}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
