# Development and validation

This repository currently contains planning documents and their validation tool.
There is no runtime to build, install or start. Commands below are separated
between **available now** and **future workflows**. See
[IMPLEMENTATION_PLAN.md](IMPLEMENTATION_PLAN.md) before starting implementation.

## Available now

From the repository root:

```sh
python tools/check_docs.py
git diff --check
git status --short
```

The checker validates local Markdown file/fragment links, task/spike/ADR
references, milestone metadata, checkbox uniqueness and the absence of checked
runtime tasks in this planning snapshot. It does not validate external source
availability, prove architecture feasibility, or render Mermaid diagrams.
As implementation starts, remove/update the snapshot-only checkbox rule with
the first legitimately completed runtime task and its evidence.

The first code task is M0.3: a repeatable, read-only environment/doctor probe.
It must not mount binderfs, enable an LSM, modify drivers, add a user to groups,
install packages or start an Android container as part of inspection.

Useful individual inventory commands (some tools may be absent):

```sh
uname -srmo
lxc-start --version
rustc --version
cargo --version
lspci -nnk -d ::03xx
pacman -Q lxc mesa nvidia-utils nvidia-open libdrm libxcb wayland wayland-protocols xorg-server
rg binder /proc/filesystems
zcat /proc/config.gz | rg 'CONFIG_(ANDROID_BINDER|USER_NS|PID_NS|NET_NS|CGROUP|SECCOMP|SECURITY_SELINUX)'
sed -n '1,2p' /sys/kernel/security/lsm
ls -l /dev/dri
glxinfo -B
vulkaninfo --summary
```

Missing config.gz is unknown configuration, not proof of missing Binder. On the
observed Linux7.2 Arch kernel, Rust Binder initializes binderfs directly. Runtime
filesystem registration and later an isolated ioctl test are more reliable than
requiring C Binder's CONFIG_ANDROID_BINDERFS. Capture active LSMs separately from
compiled-in support. Inspect whole-program command exits rather than treating a
failed optional package query as failure of every subsequent check.

The actual initial inventory is in [RESEARCH.md](RESEARCH.md). Do not add raw
Vulkan UUIDs, full environment dumps, machine names or unrelated app logs to the
public repository. Record test device model/PCI ID, kernel/module/userspace
versions and selected capabilities instead.

## Future host iteration

M1 should provide the following standard commands once a workspace exists:

```sh
# Planned, not currently executable in this repository.
cargo fmt --all -- --check
cargo clippy --workspace --all-targets -- -D warnings
cargo test --workspace
```

Hardware/container tests must be explicit and separate from default unit tests.
Use temporary managed data/runtime directories and fake adapters for host tests;
never point destructive cleanup tests at the user's real Android data. Test
helper path/UID/FD validation without root where possible; active helper tests
use a dedicated test instance and tracked resource ledger.

Thread ownership matters: one owner dispatches each XCB/Wayland connection,
daemon control work never blocks on fences, and renderer/FFI objects document
their creation/use/destruction thread. Introduce modules and dependencies only
when a selected task needs them. Every unsafe wrapper explains consumed versus
borrowed FDs and GPU object lifetime.

## Future AOSP build workflow

Do not sync/build AOSP during routine host development. Allocate a separate,
explicit checkout/output/cache path after checking upstream build requirements
and available disk/RAM. Keep it outside this repository and never use repository
root or a home directory as a cleanup target. M2 pins a supported Linux build
environment; Arch remains the reference runtime desktop.

The following is a **candidate control recipe**, not a validated build instruction:

```sh
# Run only in a dedicated AOSP source directory prepared by M2.
repo init -u https://android.googlesource.com/platform/manifest -b android-17.0.0_r1
repo sync -c -j8
repo manifest -r
source build/envsetup.sh
lunch aosp_64bitonly_x86_64-cp2a-userdebug
# M2 verifies this combo and chooses artifact/module targets before building.
```

The tag's product and cp2a release config exist; a successful lunch/build has not
been observed. Pin Repo itself and all resolved project revisions, including
prebuilts. Store resolved manifests and hashes through reviewed build tooling.
Do not substitute trunk_staging because an old tutorial used it. The DroidLayer
product definition and minimal vendor HAL closure are separate M2/M4 work.

Separate iteration loops:

| Change | Intended rebuild/redeployment |
|---|---|
| Rust CLI/daemon/X11/Wayland | Cargo only; reuse matching Android image/protocol. |
| Android platform service/Shell adapter | Targeted Soong modules; deploy matching signed artifacts and restart affected services/image as required. |
| Composer/allocator/mapper/Mesa/ANGLE | Targeted module or pinned Meson/NDK build; validate Android ABI/SELinux/linker paths; replace matching vendor artifacts. |
| Framework/SF private interfaces | Rebuild affected dependents; restart coherent service set or boot new image; run task/graphics regressions. |
| Base release/product/APEX/signing | Full affected image build and reproducibility comparison; user data compatibility audit. |
| Test APK | Pinned Android SDK/NDK build and install through the explicit development transport. |
| Packaging | Package known image/host artifacts; do not implicitly run AOSP build. |

Use `m <actual-module-name>` after a configured build, with names recorded by the
implementation task. Do not document imaginary module names as executable steps.
If adbd is temporarily needed, restrict it to an explicitly enabled development
transport; no unauthenticated TCP listener or permanent production prerequisite.

Reproducibility records include source/toolchain/build-host digests, release
flags, patch order, environment/time metadata, signing mode, image hashes and
unpacked UID/GID/mode/xattr comparisons. Two clean builds must agree; a cached
rebuild proves only cache reuse. Any nondeterminism keeps that gate open.

## Future X11 and nested Wayland testing

The developer stays on X11. M7 uses real root-child managed X11 windows; an
Xvfb/Xephyr test server plus a small WM is useful for automated protocol/lifecycle
checks, but cannot certify the real RTX GPU path.

After M0.7 installs and pins a compatible stable Weston, the intended nested
workflow is:

```sh
# Future examples; first verify the installed stable Weston's --help output.
weston -B x11 --socket=droidlayer-test-wayland --renderer=gl
# In a separate terminal, use that socket for the future Wayland test client.
WAYLAND_DISPLAY=droidlayer-test-wayland droidlayer-wayland-test
```

The named test binary is a planned test harness, not an existing command. Use a
dedicated config/socket, never overwrite the normal WAYLAND_DISPLAY globally.
Weston's renderer choice affects dma-buf/sync support. A Pixman run can validate
xdg-shell behavior; it does not count as accelerated import. Use Weston headless
for automation and a second compositor for optional-protocol/parity tests. Capture
actual registry versions and output renderer/device; don't infer them from package
names. One nested Weston window is acceptable for these Wayland tests only.

## DRM, VKMS and the single physical monitor

Render-node import/allocation tests normally coexist with the current Xorg
desktop and need no monitor switch. VKMS tests modesetting API behavior, not
physical Intel/NVIDIA rendering. Neither a headless compositor nor VKMS certifies
real GPU modifiers, scanout or explicit synchronization across driver boundaries.

Real KMS needs a card/connector/CRTC/plane and seat/lease or DRM-master ownership.
Use an unused GPU if the P530 becomes available, an appropriate lease, or an
explicitly scheduled VT test. Do not take the active Xorg GPU or change its driver
to Nouveau during ordinary tests. Cable/input switching may be useful to observe
physical output, but is not required for normal Wayland or render-node development.

## Android security test environment

Do the read-only SPIKE-010 audit first. Kernel namespaces do not create independent
SELinux policies. An enforcing integration experiment needs a host prepared for
that policy and recovery; it must not load Android policy over the developer's
current host. A reduced-MAC trusted-APK profile remains a project decision and
must be named in every result if later adopted. No public sandbox/security claim
is valid merely because the container boots.

Never allow the guest all capabilities, arbitrary device nodes, writable host
sysfs/cgroup/bpffs, raw input or the host home directory to make a test pass.
Record exact failing operations and propose scoped adaptations.

## Test layers and evidence

| Layer | Mandatory focus | Evidence needed |
|---|---|---|
| Rust unit | State, geometry, parsing, UID/device selection | Deterministic pass/fail and regression inputs. |
| IPC integration | Peer identity, FD ownership, bounds/backpressure | Truncation/invalid FD/reconnect tests and leak checks. |
| Container/Binder | Private contexts, service health, cleanup | Namespace/device audit and repeated boot/fault reports. |
| Android instrumentation | Task/activity/render/input/configuration | Test APK hashes, lifecycle counters and service assertions. |
| Headless/nested | Window protocols and task mappings | WM/Wayland properties, configure/focus/release event traces. |
| VKMS | Atomic modesetting and seat/resource handling | API/fence results distinct from physical device tests. |
| Real GPUs | GLES/Vulkan/allocator/import/modifier/sync | Hardware/provider/driver matrix; copies, GPU passes, latency and stress. |
| Recovery/security | Policy, hostile guests, crash/suspend | Denied operations, resource bounds and restoration behavior. |

Store spike results using [SPIKES.md](SPIKES.md)'s template. Do not commit binary
images, build trees, personal app data or unredacted logs. Large CI artifacts need
retention/size controls. Performance reports name workload, resolution, rate,
renderer, producer/display devices, queue depth, synchronization and measured
CPU copies/GPU passes. No specific frame-rate target is promised before baseline
measurements; a passing static frame is not a latency or sustained-load test.
