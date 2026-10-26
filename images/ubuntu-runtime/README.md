# ubuntu-runtime

Minimal Ubuntu runtime base image cut with the native [ContainerHive chisel build backend](https://github.com/ContainerHive/ContainerHive/blob/main/docs/usage/chisel.md). Contains only essential runtime libraries and tools — no package manager.

## Runtime User

The image ships a non-root user and a writable home directory:

- `runtime` - uid `1000`, gid `1000`, default login shell `/bin/sh`
- `$HOME` is `/home/runtime`, a root-owned directory with mode `0777`

## Busybox Applets

The `slices/busybox.yaml` slice overlay ships one symlink per busybox applet, so the cut installs the applets like the removed `busybox --install` step. Applet paths that another package also declares keep their alternate `/bin` or `/sbin` spelling, which resolves to the same physical file through the usrmerge symlinks. `sbin/ip` collides under all spellings and only runs via `busybox ip`. Regenerate the file with `tools/enumerate-applets.sh` after upstream changes.

## Included Tools

- **busybox** - multi-call binary providing common Unix utilities
- **ca-certificates** - TLS/SSL certificate authorities
- **libc6** - GNU C Library
- **tzdata** - timezone data

