# Architecture decision records

Accepted records state project direction, not implemented functionality. Proposed
records must not become hidden assumptions in implementation. Each includes its
validation gate; supersede or amend a disproved decision before continuing work
that depends on it. Licensing and reduced-MAC security profiles remain undecided.

| ADR | Decision | Status |
|---|---|---|
| [0001](0001-upstream-aosp.md) | Upstream AOSP, independent product | Accepted |
| [0002](0002-android-baseline.md) | Stable Android 17 baseline | Accepted |
| [0003](0003-lxc.md) | LXC system container | Proposed |
| [0004](0004-binderfs.md) | Private Binder instances through binderfs | Accepted |
| [0005](0005-rust.md) | Rust host implementation with narrow native interfaces | Accepted |
| [0006](0006-ipc.md) | Linux Unix sockets and explicit resource protocol | Proposed |
| [0007](0007-task-window-mapping.md) | Android task maps to one host top-level | Proposed |
| [0008](0008-x11.md) | Independent native X11 windows | Accepted |
| [0009](0009-wayland.md) | Native Wayland client backend with nested development | Accepted |
| [0010](0010-graphics-transport.md) | Composed outputs, dma-buf and explicit synchronization | Proposed |
| [0011](0011-privilege-separation.md) | Privileged setup separated from user/session services | Accepted |
| [0012](0012-gpu-abstraction.md) | Separate rendering, allocation and presentation devices | Accepted |
| [0013](0013-nvidia.md) | NVIDIA rendering provider is an early feasibility gate | Proposed |
| [0014](0014-selinux.md) | Resolve shared-kernel SELinux before claiming Android sandbox parity | Proposed |
| [0015](0015-dependencies.md) | Small reviewed dependency set introduced at point of use | Proposed |
| [0016](0016-licensing.md) | Recommend Apache-2.0 with explicit third-party provenance | Proposed |

For evidence see [RESEARCH.md](../RESEARCH.md) and [SOURCES.md](../SOURCES.md).
