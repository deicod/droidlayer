# DroidLayer feasibility research

Evidence cutoff: **2026-09-05**. Read with [SOURCES.md](SOURCES.md), which records
source revisions and paths. **Verified** means observed in upstream source,
specification, or the local inventory; it does not mean DroidLayer has run it.
**Proposed** is a design inference. **Needs prototype** identifies an experiment
with a pass/fail outcome in [SPIKES.md](SPIKES.md).

## 1. Feasibility conclusion

The shared-kernel runtime is credible, and both desktop protocols can represent
independent windows. The complete requested system is **not yet demonstrated**.
Its hard problems are Android task composition/export, an Android-compatible
accelerated NVIDIA rendering path, and retaining Android's security model on a
kernel whose SELinux state is shared with the host. LXC and Rust do not solve
these problems by themselves. [A04–A11, K03, G01–G08, R01–R04](SOURCES.md)

Recommended experiment: retain ART, Android WindowManager/Shell and
SurfaceFlinger; associate one application task with one dedicated composed
output; consume that output inside Android; export a described GPU allocation
and synchronization FDs to an unprivileged host presentation process. Start
with a trusted virtual display per task, but compare task mirroring and a
targeted task-composition extension before accepting this boundary. Do not
commit to a SurfaceFlinger rewrite, host Binder stack, or nested compositor as
the production X11 interface. [ADR-0007](adr/0007-task-window-mapping.md)

The first external proof is a real test APK in a separately managed X11 window
with input. Its report must identify whether rendering was accelerated. A
software proof does not satisfy the hardware milestone. Wayland protocol and
NVIDIA allocation spikes start early, before hardening the X11 implementation.

## 2. Local environment inventory

Read-only observations during this run:

| Item | Observation | Consequence |
|---|---|---|
| Repository | Only `README.md` and `docs/.gitkeep`; clean, initial commit `eef7dd3` | Documentation skeleton only; no runtime to validate. |
| Host | Arch Linux, x86_64, kernel `7.2.2-arch1-1` | Reference environment; not a portable minimum version. |
| Tools | LXC `7.0.0`, Rust/Cargo `1.98.0`; Weston absent | LXC tooling available; nested tests need a later Weston install. |
| Display | Xorg `21.1.24`, GLX display `:0`, direct rendering | Existing X11 desktop can remain the development session. |
| GPU | RTX 4070, PCI `10de:2786`, driver `nvidia`; render node present | Real NVIDIA host import/presentation spike possible without modesetting. |
| NVIDIA | `nvidia-open` and `nvidia-utils` `610.57.04`; Vulkan driver identifies as NVIDIA proprietary | Open kernel and proprietary userspace are distinct facts. |
| Intel | P530 not enumerated; `vulkan-intel` package query did not find it | Availability/firmware enablement and driver install unresolved. No Intel result claimed. |
| Graphics libs | Mesa `26.2.2`, libdrm `2.4.134`, libxcb `1.17.0`, Wayland `1.26.0`, protocols `1.49` | Snapshot for reproduction. Not all Mesa GPU drivers are installed. |
| Kernel isolation | User/PID/network namespaces, cgroups, seccomp enabled | Actual delegated permissions still need SPIKE-001. |
| Binder | `ANDROID_BINDER_IPC_RUST=y`, C Binder disabled; `/proc/filesystems` contains `binder` | Do not falsely reject this kernel for missing C Binder or `ANDROID_BINDERFS`. |
| SELinux | Compiled in; active LSM list `capability,landlock,lockdown,yama,bpf`; no mounted selinuxfs observed | Android enforcing policy is not available in the current session. |
| Host graphics query | NVIDIA Vulkan 1.4.341; dma-buf, DRM modifiers, external memory/fence/semaphore FD and foreign queue-family extensions advertised; GLES 3.2 via GLX | Extension presence is insufficient to prove any particular format/modifier/handle combination. |

No privileged changes were made. Render-node permissions are host configuration,
not a recommended DroidLayer policy. Raw diagnostic dumps with local identifiers
were not committed. See [DEVELOPMENT.md](DEVELOPMENT.md) for the repeatable audit.

## 3. Android 17 build strategy and x86_64 product

**Verified:** stable `android-17.0.0_r1` is build `CP2A.260605.016`, API 37,
security patch level 2026-06-05. The manifest tag and its peeled commit were
queried directly. This was the only Android 17 manifest release tag returned.
Use it as the initial stable base; do not follow `android-latest-release`,
Canary, `main`, or QPR betas. A June SPL is not a claim to include September
security fixes: audit subsequent published security changes separately. [A01](SOURCES.md)

**Proposed product:** `droidlayer_x86_64`, 64-bit-only, built from the selected
tag's generic AOSP system/system_ext/product components plus a DroidLayer vendor
and container product. `aosp_64bitonly_x86_64` is a useful build control; its
`core_64_bit_only.mk` inheritance fits the initial ABI. Ordinary `aosp_x86_64`
has a different 64-bit system/32-bit compatibility policy. Audit the actual
module closure before promising removal of every 32-bit artifact. [A02](SOURCES.md)

A GSI is principally a generic system image for a compatible vendor environment.
It is not a complete LXC root filesystem or a desktop GPU driver package. The
generic product includes handheld/telephony inheritance that must be audited.
Cuttlefish contributes useful reference HALs and product examples, but its VM,
virtio devices, bootloader and device assumptions must not become requirements.

The tag contains a `cp2a` release config. The candidate control build is
`aosp_64bitonly_x86_64-cp2a-userdebug`; verify it through that checkout's build
configuration before publishing an executable recipe. Merely finding the
product and release files is not a successful lunch/build. Keep release flags
fixed because Android 17 contains alternative virtual-display implementations.
[A02, A07; SPIKE-009](SPIKES.md#spike-009)

Pin the resolved multi-repository manifest, Repo tool, compiler prebuilts,
build-host package set, release config, patches, Mesa/ANGLE inputs and signing
mode. Preserve source license metadata. Two independent builds must compare
image hashes and unpacked file metadata; a tag plus a Dockerfile is not proof
of byte reproducibility. See section 22.

## 4. Binder and binderfs

**Verified:** each new binderfs mount provides private devices; its
`binder-control` supports `BINDER_CTL_ADD`, returning dynamically assigned
major/minor numbers. A separate mount is the isolation unit; differently named
bind mounts of one device do not create separate Binder contexts. User-namespace
mounts are supported; `stats=global` is restricted. Unlink removes a device name;
open references and mounts still determine resource lifetime. [K01](SOURCES.md)

Linux 7.2 supports C and Rust Binder implementations. The C path uses
`CONFIG_ANDROID_BINDER_IPC` plus `CONFIG_ANDROID_BINDERFS`; the Rust path uses
`CONFIG_ANDROID_BINDER_IPC_RUST` and initializes its binderfs implementation
directly. Confirm filesystem registration and ioctl behavior, not just a legacy
Kconfig/module name. Do not ship an out-of-tree Binder driver by default. [K02](SOURCES.md)

Proposed lifecycle: helper creates a mount in its private mount namespace for
one user instance generation, bounds device creation, allocates nodes, applies
ownership/modes and cgroup access, exposes only required nodes plus read-only
feature information to LXC, closes provisioning FDs, and retains mount ownership
until Android exits. Android may see conventional `/dev/binder` paths backed by
private devices. Never expose the control node to apps. Feature-path compatibility
with `ProcessState.cpp` must be tested. [A10, K01; SPIKE-001](SPIKES.md#spike-001)

`binder` is required for framework services and stable AIDL HALs. `hwbinder` is
needed if the built vendor service closure still uses binderized HIDL.
`vndbinder` is needed only for legacy vendor Binder services using that context.
Prefer AIDL composer/allocator and mapper5's stable C interface, but do not assert
that all inherited Android 17 HALs have migrated. Bootstrap may provision all
three privately; remove unused devices and managers only after VINTF, service,
binary dependency and boot audits. [A09–A10](SOURCES.md)

DroidLayer host code needs UAPI setup, not a Binder protocol implementation.
Android code uses AOSP-generated Java/NDK Binder interfaces internally. A private
Binder device is not itself a permission policy: Android service permissions,
UID checks and SELinux hooks remain necessary. Cross-instance context-manager
and FD-leak tests are required.

## 5. LXC boot and Android system requirements

LXC supplies PID/mount/IPC/UTS/network/user namespaces and cgroup/device controls;
it can execute Android init as container PID 1. This does not make an untouched
GSI bootable. Prefer LXC over a custom namespace runtime; systemd-nspawn/runc
offer alternatives but do not remove Android init/HAL/LSM work. [L01, R01](SOURCES.md)

**Required product audit, before disabling services:**

| Subsystem | Container-specific issue | Proposed treatment / proof |
|---|---|---|
| First-stage init/fs_mgr | Expects Android boot metadata, partition discovery, verified boot and first mounts | Helper mounts validated immutable partitions; narrow documented init entry/configuration for an already prepared root. Do not blindly pass `second_stage` and assume all setup occurred. |
| SELinux init | Loads policy and relabels resources on the shared kernel | Gate in section 18. No host-wide policy overwrite or `setenforce` from the guest. |
| `/dev`, ueventd, properties | Android ownership, sockets, property areas and coldboot expectations | Private tmpfs `/dev`, selected nodes, predictable labels/modes; constrain ueventd. Retain property service. |
| APEX/apexd/linkerconfig | Loop/device-mapper, mount namespace and activated libraries | Preserve signed APEX/APK verification. Determine which activation mounts helper can prepare; test APEX lifecycle. No assumption that copying `/system` activates ART. |
| task profiles/cgroups | Android's expected controller layouts differ from host cgroup v2 delegation | Product task-profile/controller configuration beneath an instance subtree; no writable host cgroup root. |
| vold/installd/keystore2 | Data mounts, encryption, user unlock, keys, app data ownership | Private persistent data volume; software security services may be valid for development but never report hardware backing. Retain app isolation and package verification. |
| composer/allocator/mapper | No mobile display controller/gralloc supplied by the host | Vendor implementations with boot display and virtual outputs; native GPU or renderer transport. |
| netd/BPF/connectivity | Android BPF pinning, network setup and privileged operations | Inventory required BPF/netd behavior; isolate net namespace, helper-owned network resources. Do not mount writable host bpffs. |
| power/health/thermal | Battery and mobile power controls do not exist | Minimal truthful implementations where required by VINTF; no host sysfs power control. |
| radio/GNSS/sensors/NFC | Unavailable hardware and feature dependencies | Omit features and services only after dependency audit; do not falsely advertise hardware. |
| media/audio/camera | Framework may need services even before real device bridges | Keep minimum service closure and honest unavailable devices; software codecs acceptable; real audio/camera later. |

The init conclusions are grounded in the selected tag's entrypoint, SELinux and
APEX source. Individual HAL removal and BPF adaptations remain **Needs prototype**;
their exact closure cannot be established without product generation/build and
boot logs. [A09, A11, A13; SPIKE-001, SPIKE-009, SPIKE-010](SPIKES.md)

Preserve servicemanager, system_server, Zygote64, ART, SurfaceFlinger, package,
activity, window, input and display services, logd, and the dependencies needed
for their health. Define readiness as service operations plus a usable unlocked
Android user; `sys.boot_completed=1` alone is insufficient.

## 6. Android graphics pipeline and allocation

An app can produce several surfaces: ordinary UI, SurfaceView/video, dialogs,
effects and child surfaces. WindowManager controls hierarchy and visibility;
SurfaceFlinger consumes layer buffers and composes outputs, with the composer
HAL and RenderEngine deciding device/client composition. A Task is a management
container, not a ready-made pixel allocation. [A04–A09](SOURCES.md)

BufferQueue has ownership and backpressure: do not attach a second consumer to
an app's queue and steal buffers from SurfaceFlinger. A SurfaceControl leash
controls a subtree; it is not a dma-buf handle. `AHardwareBuffer`/`GraphicBuffer`
wrap native handles whose integer fields and FDs are allocator-specific. The
host must receive explicit plane/format/modifier metadata, not reinterpret an
Android native_handle as a portable C structure. [A04, A08–A09](SOURCES.md)

**Proposed ownership:** Android allocator/mapper is the authoritative Android
allocation API. A native Mesa provider may allocate through the selected render
node. A forwarded NVIDIA provider requests allocations from a host Vulkan worker
and wraps them in the guest allocator/mapper. Both must negotiate output-import
constraints before allocation. The guest output consumer owns BufferQueue slots;
the host borrows exported allocations until it returns a release fence. Generic
host graphics code owns imported GPU objects, not Android object lifetimes.

Start with SDR RGB/RGBA, explicit plane layouts and a small bounded buffer pool.
YUV, color management/HDR and protected content require separate capability
contracts. Secure/protected layers must be refused or blanked; neither mirroring
nor export may bypass Android content protection.

## 7. Candidate graphics boundaries

These are distinct output boundaries; choosing a rendering provider is a second
decision. All candidates retain an actual AOSP runtime and unmodified test APKs.

| Model | Mechanism / AOSP changes | Costs, compatibility and risk | Status |
|---|---|---|---|
| A1 | One trusted virtual display per task; Shell/ATMS launch/reparent coordination; guest output consumer; vendor HALs | Uses normal display composition; likely one SF GPU composition pass, then zero or one host GPU pass. Secondary-display behavior, extra tasks on a display, IME and display-count/resource policy are risks. | **First spike recommendation**, not accepted architecture. |
| A2 | Keep tasks on a common freeform display; mirror/crop a task subtree to an output | Less task display migration; private SurfaceControl/SF integration and refresh/occlusion behavior need proof. Cropping cannot safely assign IME, overlays or sibling windows automatically. May duplicate composition. | Compare in SPIKE-002. |
| B | Export app SurfaceControl buffers through a service | No universal composed task buffer at this boundary. Needs ownership changes or parallel layer consumption and a compositor for child surfaces/effects. Low-copy potential; high synchronization/security risk. | Reject as stated; only reconsider as a fully specified layer protocol. |
| C | WM/Shell tags tasks; modified SF/composer exports a per-task layer set; host composes | Rich metadata and potential direct presentation. Must transport transforms, clips, z-order, damage, alpha, fences and task associations; recreate effects, protected-layer policy and overlays. Generic HWC layers are not stable Task IDs. | Plausible alternative; higher maintenance and host complexity. |
| D1 | Targeted SF extension: compose one task subtree to a dedicated BufferQueue while retaining normal display placement | Single output, avoids wholesale compositor duplication; requires private SF frontend/CompositionEngine changes and explicit handling of non-task layers. | Fallback if A1/A2 fail; compare patch/rebase cost. |
| D2 | Small guest Wayland server/proxy forwarding one surface tree per task to XCB/Wayland | Can reuse client/server concepts and direct subsurfaces. Still requires correct Android task/layer attribution and X11 rendering; making it a general compositor adds scope. | Not selected merely because Waydroid is Wayland-based. |

Latency and copy counts above are **hypotheses**, not measurements. A composed
buffer exported without CPU copying still incurred composition; an X/Wayland
compositor may perform another GPU pass. Native NVIDIA versus Mesa affects
allocation/rendering at every boundary, not merely the final window backend.

For security and maintenance A1 offers the smallest initial ownership surface:
Android composes Android semantics; a narrow guest adapter exports a known output.
For maximum efficiency C may eventually remove a composition pass, but it would
make DroidLayer responsible for more of Android's layer semantics. Spikes must
record CPU copies, GPU passes, frame age, queue depth, modifier/fence support,
patch paths and unmodified-APK behavior before promoting an ADR. [A04–A09, R02](SOURCES.md)

## 8. Task-to-window lifecycle, dialogs and resize

**Verified:** `TaskOrganizer` registers for initial tasks and appeared/vanished/
info changes with a SurfaceControl leash. `ShellTaskOrganizer` already dispatches
listeners and manages ownership. Prefer integrating a DroidLayer listener into
the product Shell over registering a competing organizer that disrupts its
existing desktop/freeform/PiP/split-screen ownership. These are privileged,
platform APIs, not a stable third-party SDK. [A04–A05](SOURCES.md)

Use `(instance generation, Android user, task ID)` as runtime identity, with a
separate generation for reused task/display/buffer IDs. Package name cannot
identify a task: two tasks of one package need separate windows. Track leaf
application tasks versus organizer-created root/container tasks. Resnapshot
after reconnect and reconcile sequence-numbered deltas. Resolve events during
launch/reparent/transition, not just steady-state callbacks.

For A1, launch via trusted display options and reconcile tasks that launch other
tasks, reuse an existing task, or move to the default display. Android can place
multiple tasks on one display; one display per task is **DroidLayer policy that
must be enforced**, not automatic AOSP behavior. Keep a control/default display
for required system UI; it is not the final host application window.

Host resize is a request: assign a configure serial, resize the virtual display
and task bounds through Android display management and WindowContainerTransaction,
propagate density/insets, wait for a matching configuration/buffer generation,
and retire old buffers after release. Preserve letterboxing for non-resizable
apps. Host coordinates exclude decorations and apply inverse crop/scale/rotation
to reach Android display pixels. Do not fake a resize with permanent image scaling.

| Android surface class | Initial proposed host treatment | Required evidence |
|---|---|---|
| Activities within one task | One host top-level; activity transitions remain inside | Launch modes, back stack, rotation and process recreation. |
| Dialogs/PopupWindow/SurfaceView | Composite into owning task output | Outside-bounds popups, dim/blur, video and clipping. |
| Separate application task | Separate host top-level | Explicit new-task, document mode and cross-app intents. |
| IME | Prefer correct guest IME on the focused task display initially | IME may live outside the task subtree; display policy, insets and text entry must pass. |
| Permission/system dialogs | Explicit guest-owned presentation with correct modality/parent association | Never silently crop away permission prompts or expose them under another app's identity. |
| Toast/overlay/PiP | Enumerated policy, initially conservative | Ownership and global/system layers cannot be guessed from layer names. |

Moving/minimizing/focusing a host window must update the task/display lifecycle
without assuming minimized means destroyed. Wayland does not guarantee a client
can observe every minimized/occluded state; throttle by callbacks and policy,
never infer app destruction from missing frames. [G03](SOURCES.md)

## 9. Native X11 integration

Use XCB-compatible interfaces from Rust. `x11rb` can speak X11 in Rust or provide
an XCB-backed connection; the latter is a candidate for Vulkan
`VK_KHR_xcb_surface`. Keep XCB lifetime/FFI inside the backend. The `xcb` crate is
a maintained alternative. Xlib is not an architectural requirement.
[DEPENDENCIES.md](DEPENDENCIES.md), [ADR-0008](adr/0008-x11.md)

Create a normal InputOutput child of the root with `override_redirect=false` per
task. Set WM_CLASS, UTF-8 title, WM_PROTOCOLS (`WM_DELETE_WINDOW`, focus protocol
where appropriate), WM_NORMAL_HINTS, `_NET_WM_PID`, `_NET_WM_WINDOW_TYPE`, icon,
and applicable EWMH state/activation properties. Follow WM focus timestamps and
ConfigureNotify; distinguish content geometry from frame extents. Let the WM
manage decorations, workspaces and taskbar. Close requests target the task, not
unconditionally force-stop every process in the package. [G01](SOURCES.md)

Presentation choices:

- Prefer proving import into host Vulkan/EGL followed by a GPU draw to an X11
  swapchain. One host GPU pass is acceptable near-zero-copy; no readback/encoding.
  Vulkan WSI is useful when direct DRI3 support differs between Xorg drivers.
- Test DRI3 multi-plane/modifier pixmap import plus Present for compatible buffers.
  Query server extension versions/capabilities. DRI3/Present 1.4 syncobj paths
  cannot be assumed because protocol XML is installed. Older X Sync fences are
  not interchangeable with Linux sync_file FDs.
- Xorg compositing/unredirect and the WM determine final copies/scanout. Report
  observed behavior; never promise universal zero-copy X11.

[G02, G04–G05; SPIKE-004](SPIKES.md#spike-004)

## 10. Native Wayland integration

DroidLayer is a Wayland **client**. One `wl_surface` + `xdg_surface` +
`xdg_toplevel` per task; set title/app_id and optional parent relationships.
Handle initial configure before buffer commit, acknowledge serials, honor size
constraints and compositor-driven state. Implement client decorations when no
server decoration protocol is offered. Taskbar/workspace placement ultimately
belongs to the compositor. [G03](SOURCES.md)

Use linux-dmabuf feedback to select compatible device/format/modifier tranches,
then create/import wl_buffers. Prefer `linux-drm-syncobj-v1` when supported;
negotiate legacy explicit-sync or a proved implicit-sync path otherwise. With
syncobj synchronization, the release timeline point is authoritative; do not
reuse on an unrelated `wl_buffer.release` or frame callback. Output scaling,
fractional scale, viewport transforms and configure generations belong in the
backend-to-core geometry contract. [G03–G05](SOURCES.md)

Develop under Weston `-B x11` in the existing X11 session. A nested compositor
window is appropriate for testing Wayland clients; it is not the X11 product
backend. Exercise Weston plus another compositor before parity claims.

## 11. dma-buf contract and synchronization

The wire buffer description needs: allocation ID/generation, producer device
identity, dimensions, DRM fourcc, modifier, plane count, per-plane FD index,
offset/stride, plane allocation sizes where available, usage, color/dataspace,
crop/transform, alpha semantics, damage and explicit acquire synchronization.
Check bounded counts, arithmetic overflow, actual handle properties and negotiated
capabilities. Multi-plane formats may share one FD; an FD's existence alone
does not establish image importability. [K04, G04–G05](SOURCES.md)

Proposed first synchronization currency is Linux **sync_file** FDs, matching
Android acquire/release fences. A frame transitions from producer ownership to
consumer ownership only after acquire; a buffer becomes reusable only after
every consumer's release dependency completes. Import/export FD ownership differs
across EGL/Vulkan APIs; wrappers must record whether each call consumes or borrows
an FD. Use OwnedFd/BorrowedFd and atomic CLOEXEC receipt. [K04, G04](SOURCES.md)

The host may convert sync_file to DRM syncobj timeline points for presentation
and export completed dependencies back to Android. Do not confuse Vulkan opaque
FDs, sync_file FDs and DRM syncobj FDs; capability bits and temporary/permanent
payload semantics differ. No CPU fence wait on the event thread. An asynchronous
wait fallback may prove correctness but must be measured and identified; it does
not justify advertising a fully explicit GPU path. [K04, G03–G05](SOURCES.md)

Frame callbacks/presentation timestamps pace work; they do not release buffers.
On failure or disconnect, do not immediately recycle buffers still used by the
GPU/compositor. Drop unsubmitted queued frames with ownership accounted for,
bound outstanding resources, and quarantine uncertain generations until consumers
are destroyed and dependencies complete.

## 12. NVIDIA feasibility and exact Waydroid limitation

**Verified locally:** RTX 4070 rendering works in host GL/Vulkan; required-looking
external memory/modifier/fence extensions are enumerated. NVIDIA documents GBM,
DRM/PRIME and explicit synchronization support. **Not verified:** Android-created
or host-allocated image compatibility for the DroidLayer pipeline. [G07–G08](SOURCES.md)

Waydroid's current host GPU selector explicitly excludes the `nvidia` kernel
driver. Its Android Mesa/GBM approach needs an Android/Bionic GPU driver that
implements that kernel API. Host NVIDIA GL/EGL/Vulkan libraries use the GNU/Linux
userspace environment and cannot simply be loaded as Android vendor HALs. Opening
a render node or enabling GBM does not provide that missing driver. Open NVIDIA
kernel modules keep NVIDIA's userspace contract; NVK targets Nouveau, not a
drop-in replacement userspace for `nvidia-open`. [R01, G06–G08](SOURCES.md)

Thus the blocking problem is **guest rendering/allocator interoperability**, plus
presentation/sync compatibility, rather than a blanket lack of NVIDIA Wayland
support. Old issue comments about missing GBM are not a current architectural
basis. Three routes deserve explicit treatment:

| Route | Suitability on the current Xorg/NVIDIA desktop | Gate |
|---|---|---|
| Guest Mesa Intel/AMD → host NVIDIA presenter | Could preserve current desktop if Intel becomes available; cross-GPU import or GPU copy needed | Cannot assume PRIME supports every modifier/direction. Test P530→RTX separately. |
| Guest Mesa NVK/Zink on Nouveau | Native Bionic route worth later support on appropriate systems | Would require changing ownership/driver of the RTX; does not satisfy current `nvidia-open` desktop setup. No automatic switch. |
| Guest Venus + GLES via ANGLE → isolated host Vulkan renderer | Most relevant RTX rendering candidate; same host NVIDIA device can allocate/export buffers | Transport, AHB/gralloc, sync-FD, format/texture features and renderer sandbox must pass. |

The current `waydroid-nvidia` project demonstrates a reported implementation of
the third shape without a VM. Source inventory shows custom vtest sync_file,
dma-buf import, host allocation and AHB patches; its published setup has
compositor/multi-GPU limitations and relies on open NVIDIA kernel modules.
This improves feasibility evidence but does **not** establish upstream Mesa
Venus as a turnkey Android 17 driver or certify DroidLayer. [R04](SOURCES.md)

Investigate Vulkan-format capabilities (including texture compression), external
handle import/export, memory type selection, foreign queue ownership and
modifier-specific image creation. A host Vulkan renderer can be backed by Mesa
or NVIDIA behind one abstract provider contract, but the guest native and
forwarded providers need different implementations. Never emulate missing
capabilities by lying to APKs. Test renderer failures as untrusted GPU command
input; do not place a command decoder in the privileged helper.

**Biggest NVIDIA risk:** a maintainable accelerated Android 17
Venus/allocator/synchronization stack on the proprietary userspace driver, not
creating an X11 window. [ADR-0013](adr/0013-nvidia.md), [SPIKE-005](SPIKES.md#spike-005)

## 13. Intel/Mesa reference path

P530 is the planned older Intel reference, requiring actual device availability
and the appropriate Mesa Android build. Prove GLES and Vulkan capabilities
separately; do not infer contemporary extension coverage from another Intel GPU.
Build Bionic Mesa userspace and allocator/mapper for the selected DRM driver;
host Arch `.so` files are not guest binaries. AMD requires its own test hardware
or external evidence before support claims. [G06](SOURCES.md)

Use the same output descriptor, fence and host presentation interfaces as NVIDIA.
Keep three GPU identities visible: Android rendering device, exported allocation
device, and host presentation device. Linear layout can be a useful cross-GPU
candidate but is not universally importable or optimal. Report each tested
direction and whether conversion was a GPU copy, CPU copy, or unsupported.

## 14. Input injection and routing

Use host-window keyboard/pointer events → normalized protocol → privileged
Android adapter → InputManager/WindowManager. Android 17 enforces
`INJECT_EVENTS` and has focused-display/target-UID controls. Bind events to a
known task/display generation and authorized focused seat; reconcile focus and
geometry before dispatch. Do not expose `/dev/input/*`, host uinput or raw
keyboard devices to the guest for ordinary nested operation. [A12](SOURCES.md)

Separate physical key events, logical text input and shortcuts. Plan XKB layouts,
compose/dead keys, repeat, modifiers, IME, pointer hover/buttons, high-resolution
scroll, relative motion/capture, touch, cancellation on focus loss and monotonic
timestamps. Pointer capture uses X11 mechanisms or Wayland relative-pointer/
pointer-constraints capability negotiation; it must release on focus loss/crash.
Initial simple key/button support is enough for the first window, not robust
international text input. [G03, R02; SPIKE-006](SPIKES.md#spike-006)

## 15. Host/guest IPC

Prefer private pathname **AF_UNIX SOCK_SEQPACKET** sockets with bounded messages
and SCM_RIGHTS. They match a shared kernel and carry dma-buf/sync_file/memfd FDs.
`SO_PEERCRED` plus helper-provisioned endpoint ownership and instance credentials
identify the guest service; account for namespace UID/PID translation. A Unix
socket path should be bind-mounted into the container without exposing the
whole host runtime directory. Separate control and frame queues avoid frame
backpressure starving lifecycle operations. [K07](SOURCES.md)

Proposed v1 control codec: a fixed bounded header plus versioned JSON payload,
using generated/validated message definitions on both sides. No serialized raw
pointers, process-local FD numbers or C layouts. Maximum message size, FD count,
sequence rules, resource quotas, peer role and major/minor negotiation are
specified before implementation. A future binary codec requires measurements,
not aesthetics. memfd carries immutable bulk metadata/test frames; it is not
automatically a GPU allocation. [ADR-0006](adr/0006-ipc.md)

Alternatives: SOCK_STREAM is workable with careful ancillary-data framing;
Binder RPC could reuse AOSP machinery but adds platform coupling; kernel Binder
crossing the boundary exposes Android IPC unnecessarily. vsock targets VMs and
provides no benefit here; loopback modes do not create per-container identity
or solve FD transfer. D-Bus is appropriate for host services/portals, not the
bulk graphics channel. A Venus transport is a separate renderer protocol, not
an excuse to expand the DroidLayer control protocol into a GPU command language.
[K07, A10](SOURCES.md)

## 16. Privilege separation

Proposed processes: system helper for validated container/device/network setup;
unprivileged per-user daemon for lifecycle policy; unprivileged session process
for desktop connections/presentation/input; separately sandboxed renderer workers
when forwarding GPU commands. The CLI never needs root. The daemon can remain
unprivileged because mounts/cgroup/device access are helper responsibilities;
prove this by tracing operations in SPIKE-001. [L01, K05](SOURCES.md)

Use systemd system/user units and a narrow helper API. Authenticate caller UID
over a system socket or D-Bus; Polkit may authorize privileged start/config
actions for a local user without handing out an arbitrary root command channel.
Fix image roots, node selection, namespace targets and mounts in helper policy.
Do not accept arbitrary LXC snippets, hooks, paths, shell commands or capabilities.
Use no-follow/openat-style path handling, immutable images and per-user quotas.

Prefer an unprivileged LXC user namespace with non-overlapping subordinate IDs.
Android's single-user UID space extends beyond a conventional 65,536-ID map;
inventory AIDs, isolated/sandbox UIDs and supplementary groups before allocating
at least the full required range. Mapping host UID directly to guest system/root
is not necessary. Android profile support later expands this mapping problem.

Drop capabilities based on observed boot requirements; cgroup v2 device controls,
seccomp, read-only mounts and namespace restrictions complement Android per-app
UID/permission isolation. GPU ioctl exposure remains a kernel attack surface;
render nodes avoid KMS ownership but are not a complete sandbox. A forwarded
renderer reduces direct guest GPU access while adding a command decoder attack
surface. X11 session clients also have the usual X11 trust limitations.

## 17. Minimum exposed resources

Start with private Binder devices, minimal pseudo-devices, isolated sockets and
either selected render nodes or a renderer socket. Guest graphics must not
require DRM master or card-node modesetting. If a driver needs additional devices,
record exact paths/ioctls and justify them; never allow all `/dev/dri` or
`/dev/nvidia*` as a convenience. Session display and desktop bus sockets remain
host-side. No host home directory, camera, microphone, input devices or clipboard
access is implicit in starting Android.

Both a malicious APK and a compromised guest service are in the threat model.
The helper must assume all IPC payloads and passed FDs are hostile. A same-UID
host process has ordinary session privileges; stronger host-to-host isolation
is not claimed. Multi-user tests must prove Binder, data and network resource
separation independently of a friendly CLI.

## 18. SELinux: a requirement conflict, not late hardening

**Verified constraint:** v7.2 SELinux uses global state; Android init loads a
policy. Mount/PID/user namespaces do not provide independent Android SELinux
policy instances. The current host has no active SELinux. Therefore unchanged
Android enforcing SELinux in a stock container on this desktop cannot simply
be enabled independently. Loading guest policy would affect the shared host
kernel. [K03, A11, A13](SOURCES.md)

This conflicts with preserving Android's full normal sandbox while targeting
arbitrary GNU/Linux desktops. Smallest proposed scope adjustment: make an
explicit **integrated host MAC policy** a prerequisite for a production enforcing
profile, while investigating whether Android per-app domains/Binder labels can
coexist with host policy and subordinate UIDs. Host policy remains host-owned;
guest init must not load/replace it. This is significant distro integration and
may fail the portability goal. [ADR-0014](adr/0014-selinux.md)

A reduced-MAC development profile for trusted test APKs could permit an early
graphics proof, but it weakens a stated requirement and is **Proposed, not
authorized as a default**. Do not implement or silently select it until the
policy decision is explicit. Preserve UID separation, permission checks, seccomp
and signing in any such experiment; permissive SELinux is not equivalent to
enforcing. Do not disable host SELinux/AppArmor or invent SELinux namespacing.

SPIKE-010 must first produce a concrete policy feasibility result. If neither
host-integrated enforcement nor an acceptable future kernel mechanism works,
report the mission constraint conflict. A VM would isolate policy but violates
the runtime model and is not the recommended silent fallback.

## 19. Networking

Initial boot/install/test APK can be offline. Later use a private network
namespace, helper-managed veth and dedicated bridge/subnet/NAT rules with explicit
ownership and conflict detection; use distro firewall integration and restore
only project-owned resources. Host network namespace sharing is not the default.
Android netd/connectivity/DNS must observe a real usable network, not just an
`ip addr` assignment. [L01, K05, A13, R01](SOURCES.md)

Audit BPF loaders, cgroup hooks, socket marking, DNS and IPv6 in the selected
product. Some required operations may need helper mediation or narrow product
changes even in an unprivileged LXC. Do not grant global CAP_BPF/CAP_SYS_ADMIN
or writable host bpffs blindly. Test offline start, DNS failure, VPN host routing,
firewall coexistence and isolation. User-mode networking is an alternative if
it preserves Android connectivity semantics and acceptable performance.

## 20. Filesystem and persistent instance strategy

One persistent instance per Linux UID, not per APK. Store immutable versioned
images in a helper-owned image store; per-user Android data in a private managed
volume. Expose guest paths for system/system_ext/product/vendor/data/metadata and
APEX activation, preserving modes, xattrs and required labels. Treat update and
rollback of data separately from image switching; older images may not read
migrated data safely. [A02, A11](SOURCES.md)

Use atomic image installation with hashes/signatures and immutable selection.
Reject user-modified privileged image hooks or unsafe archive paths. Keep guest
rootfs writable mounts narrow. Host file sharing later goes through explicit
directories or mediated document access, retaining Android scoped-storage
semantics; mounting the entire home directory would defeat the boundary.

## 21. License recommendation and provenance

Recommend Apache-2.0 for original DroidLayer code/documentation: explicit patent
terms, a good fit for upstream AOSP contributions, and compatibility with the
shortlisted permissive Rust dependencies. This remains a recommendation, not a
license grant. No LICENSE file is installed in this research run. [ADR-0016](adr/0016-licensing.md)

AOSP is mixed-license, although much framework code is Apache-2.0. Waydroid host
code is GPLv3; inspected hardware files are individually MIT or Apache-2.0. Do
not classify an entire ecosystem by one repository's badge. LXC library terms
are LGPL-2.1-or-later; dynamic linking and distribution obligations need review
if FFI is selected. Linux UAPI headers with Linux-syscall-note do not impose
kernel implementation licensing on ordinary userspace merely using syscalls.
[A14, L01, K08, R01–R02](SOURCES.md)

Record source/revision/license for patches, bindings and generated protocol
code; preserve notices and upstream license obligations. Study GPL behavior but
implement independently from APIs/specifications. No code was copied in this
run, and the same applies to the mixed-license NVIDIA reference. Do not bundle
NVIDIA proprietary components without a specific redistribution review. License
compatibility must be checked against the actual dependency graph before release.

## 22. Reproducibility and fast iteration

Separate five artifacts: base AOSP images, Android adapter/HAL modules, host
Rust binaries, packages, and test APKs. Rust edits must not trigger Repo sync or
Soong. After one configured AOSP build, use targeted Soong `m <module>` builds
for the adapter/HAL and redeploy only affected partitions/components when ABI
and signing permit. Framework/SF changes may require service restart or new
images; never promise hot-swapping private ABI changes safely. Mesa's Android
Meson/NDK path can reduce driver iteration cost but still needs pinned inputs
and a tested product integration. [A03, G06](SOURCES.md)

Arch is the runtime/reference host. Use an upstream-supported, pinned Linux
build environment for the large AOSP build when that reduces Arch tool drift;
a documented chroot/container is acceptable, not an elaborate nested build
platform. Record hardware/storage requirements from upstream and local disk
capacity before downloading. Cache source downloads, object outputs and driver
builds by input digest; an optional compiler cache is an optimization, not a
reproducibility guarantee.

Capture resolved manifest, release flags, patches, host package versions,
toolchain digests, build timestamps/identifiers, locale/timezone, module graph,
signing keys mode and artifact hashes. Rebuild unsigned/development artifacts
twice in clean outputs, explain every difference, and separately verify signed
release artifacts under controlled signing. Publish SBOM/notices and source
availability for distributed components. **None of these build results exists yet.**

## 23. Development and test strategy on one X11 monitor

| Test | Can run in existing X11 session? | What it does not prove |
|---|---|---|
| Rust unit/IPC tests | Yes; no Android image | Android boot or GPU behavior. |
| Container boot/services | Yes, after setup/security gates | Window semantics. |
| X11 windows + test WM in Xephyr/Xvfb | Yes | Real GPU Present/import; Xvfb is often software. |
| Real Xorg native task windows | Yes | Other WMs/drivers or Wayland protocols. |
| Weston X11 backend | Yes, one nested window containing Wayland test clients | Independent X11 product windows, direct scanout, DRM leasing or compositor parity. |
| Weston headless | Yes | Physical display/GPU or driver modifier behavior. |
| Render-node GPU import tests | Yes, usually no DRM master | KMS connector/plane behavior. |
| VKMS | Yes, with isolated setup | RTX/P530 acceleration, physical scanout or proprietary driver correctness. |
| Real DRM/KMS | Only on an unused GPU/lease/seat or during an explicit VT session | Cannot take the desktop's DRM master concurrently by assumption. |

[G09, K06](SOURCES.md). Weston stable version/backend capabilities must be pinned;
the live documentation's 16.0.90 is a development snapshot, not a selected build.
Review wlroots' renderer/allocator/backend boundaries for separation principles,
but do not depend on a full compositor framework to implement a client.

Create a deterministic DroidLayer test APK with activities in one task, explicit
new tasks, dialogs/popups, SurfaceView, GLES/Vulkan patterns, keyboard/pointer
logging, resizing/orientation/configuration callbacks and lifecycle counters.
Use host assertions plus Android instrumentation; include secure-layer negative
tests. Real GPU tests record driver/module, renderer, format/modifier, fence
path, copy count and latency. Random third-party APKs are supplementary only.

## 24. Reference-project assessment

Waydroid verifies the broad LXC/Binder/full-Android shape and illustrates lifecycle,
network/device setup. Its multi-window source demonstrates layer-to-task grouping
and separate IME handling. Adopt the lesson that Android and host lifecycle must
cooperate. Do not inherit layer-name parsing, global Binder fallback, Lineage
patch closure, legacy HWC1 assumptions, broad device exposure or Wayland-only
host coupling. Its security patches must be treated as requirement tradeoffs,
not harmless boot fixes. [R01–R02](SOURCES.md)

Anbox provides historical evidence for separating a system container manager,
session UI and forwarded rendering. Its archived Android 7.1.1/emugl design is
not a maintained Android 17 solution. Archival demonstrates maintenance risk;
it does not establish a single technical cause of project failure. [R03](SOURCES.md)

Mesa/ANGLE/Venus and the current NVIDIA experiment are more relevant rendering
components than reviving old emugl. NVIDIA experiment patches are a map of
missing functionality to verify and possibly upstream independently. Sommelier
illustrates window/scale forwarding, but its ChromeOS and Wayland-host direction
does not provide Android task extraction. Cuttlefish HALs are useful AOSP
references with hardware/VM assumptions to remove, not a runtime requirement.
Weston is a test compositor; wlroots is an architecture reference, not a selected
general-purpose compositor dependency. [G06, G09–G10, R04–R05](SOURCES.md)

## 25. Critical question disposition

| # | Question | Answer or falsifiable gate |
|---|---|---|
| 1 | Cleanest task integration point? | Proposed Shell task listener + SF composed virtual output; compare A1/A2/D1 in SPIKE-002. |
| 2 | Reliable task lifecycle? | Organizer initial snapshot + callbacks verified; transitions/root-vs-leaf/reconnect require SPIKE-002. |
| 3 | Obtain rendered task buffer? | A task leash is not a buffer. Guest consumer of a task-associated SF output, SPIKE-002/003. |
| 4 | Export without CPU copies? | dma-buf mechanism exists; allocator/driver/output combination unproved, SPIKE-003/005. |
| 5 | Who allocates? | Android allocator API with native-Mesa or host-renderer provider; negotiate host import constraints first. |
| 6 | Transfer synchronization? | SCM_RIGHTS sync_file; adapt to GPU waits and presentation timelines. SPIKE-003/004/005/007. |
| 7 | Host resize → Android? | Display resize + task bounds/configuration + serial/generation protocol; SPIKE-002/006. |
| 8 | Dialogs/popups/IME? | Composite task-local content; explicit display/system-layer policy, must pass SPIKE-002. |
| 9 | Input coordinates/events? | Backend transform → display/task generation → privileged Android injection; SPIKE-006. |
| 10 | Common NVIDIA/Mesa architecture? | Shared descriptor/presentation contract, different rendering/allocation providers; SPIKE-005. |
| 11 | X11 near-zero-copy? | GPU import + WSI blit is candidate; DRI3 direct path optional and capability-gated, SPIKE-004. |
| 12 | AOSP changes? | Product/vendor/init integration, Shell adapter, allocator/composer, possibly SF extension and network/LSM adaptation. Exact patch set is SPIKE-009/010 plus graphics results. |
| 13 | Small rebaseable patch set? | Not proved. Count touched private interfaces and perform a later rebase rehearsal; prefer no Bionic/ART changes. |
| 14 | Broken HAL assumptions? | Physical composer/allocator, power/health, key hardware, audio/camera and possibly legacy HIDL; closure audit SPIKE-009. |
| 15 | Services expecting mobile hardware? | Table in section 5; prove required/optional status through manifests and boot, not a guessed disable list. |
| 16 | Safe service removal? | No fixed minimum known. Minimize after baseline health, one feature closure at a time. |
| 17 | Small binderfs helper? | UAPI supports it; private mount/device/cleanup and UID mapping proof SPIKE-001. |
| 18 | Fully unprivileged main daemon? | Recommended split permits it; trace/audit proof SPIKE-001 and M3. |
| 19 | Minimum GPU/input attack surface? | Selected render nodes or renderer socket; no guest host-input nodes; resource/IPC limits from first implementation. |
| 20 | Exact NVIDIA obstacle and avoidance? | Android/Bionic driver + allocator/fence path absent from standard Waydroid NVIDIA route. Forwarded host Vulkan is plausible, with current experimental evidence, not yet validated for AOSP17. |

## Confirmed

- Stable AOSP17 tag/build and x86_64/64-bit-only source product exist.
- Binderfs supports private device instances; current Arch Rust Binder registers it.
- Android17 task callbacks, transaction controls and composed virtual-display
  buffer/fence paths exist in upstream source.
- X11 and Wayland support independent managed top-levels; nested Weston supports
  development inside an X11 desktop.
- Host RTX acceleration/external-memory extensions are available locally.
- SELinux policy is not independently namespaced by these Linux container namespaces.

## Likely

- Rust + narrow helper + LXC can provide lifecycle and private resource management.
- Task-associated SF output can support ordinary unmodified test APKs with modest
  Shell/product integration, subject to display/IME behavior.
- A host Vulkan presenter can provide near-zero-copy X11 output; Mesa native and
  NVIDIA forwarded rendering can share the output contract.

## Needs Prototype

- [SPIKE-001–010](SPIKES.md): container/Binder, task output, allocation/fences,
  native X11, NVIDIA renderer, input, nested Wayland, multi-GPU, product/HAL closure,
  and integrated SELinux policy.
- Reproducible image builds, multi-window semantics, Android BPF/APEX constraints
  and per-app security under subordinate IDs.

## Blocked / Unknown

- No Android image built/booted; no graphics or security spike executed.
- Full enforcing Android MAC on a stock non-SELinux Arch session is not available;
  production host integration remains unproved and a reduced-MAC profile is undecided.
- The P530 is not currently enumerated; AMD test hardware is not identified.
- Exact allocator/renderer patch set, NVIDIA binary redistribution needs and
  sustained cross-release AOSP maintenance cost are unknown.
