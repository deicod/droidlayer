# DroidLayer

DroidLayer is a planned native Android application runtime for GNU/Linux. It
aims to run upstream AOSP in a system container sharing the Linux kernel, with
each Android task represented by an independently managed desktop window.

**Status: feasibility research and architecture planning. No runtime, CLI,
Android image, or demonstrated application compatibility exists yet.**

The intended interface is:

```sh
# Future interface — these commands are not implemented.
droidlayer start
droidlayer install example.apk
droidlayer launch org.example.app
```

The target is one persistent Android instance per Linux user, initially
x86_64, with Rust host components, LXC, private binderfs devices, and accelerated
graphics. X11 and Wayland are equal architectural targets. The first application
window will be demonstrated on an existing X11 desktop; nested Weston permits
Wayland development there. Standalone DRM/KMS is a later experiment.

The proposed graphics boundary retains Android WindowManager and SurfaceFlinger,
combines task lifecycle integration with composed display output, and transfers
buffers and synchronization through Linux file descriptors. This is a hypothesis
to validate, not an implemented design. NVIDIA Android rendering and Android
SELinux enforcement on a shared desktop kernel are explicit feasibility gates.

Initial non-goals include ARM translation, Google services/Play Store, integrity
bypasses, protected streaming, and Windows/macOS. Intel, AMD, and NVIDIA are
required long-term GPU targets; none is currently certified by DroidLayer.

Start with the documentation:

- [Research and evidence](docs/RESEARCH.md)
- [Architecture](docs/ARCHITECTURE.md)
- [Implementation plan and agent workflow](docs/IMPLEMENTATION_PLAN.md)
- [Targeted technical spikes](docs/SPIKES.md)
- [Architecture decisions](docs/adr/README.md)
- [Development and validation](docs/DEVELOPMENT.md)
- [Source register](docs/SOURCES.md) and [dependency review](docs/DEPENDENCIES.md)
- [Critical review and handoff](docs/REVIEW.md)

DroidLayer is an independent project, not a Waydroid fork. Reference projects
are studied with source provenance recorded; no implementation has been copied.
Apache-2.0 is the [proposed project license](docs/adr/0016-licensing.md).
No project license has been adopted yet; third-party licenses remain their own.
