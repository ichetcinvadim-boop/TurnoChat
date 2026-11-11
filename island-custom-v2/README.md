# Island Custom v2

This branch is an isolated file distribution for Island-Custom-v2.exe. Do not merge into main.

The binary was split into 17 Base64 text fragments under `island-custom-v2/parts/` due to upload-size limits. GitHub Actions reconstructs the original executable, verifies SHA-256, then publishes the exact EXE to a release.

Expected SHA-256: `7479b9f3990df739ca55c40c063cd1af3ac6d98d3a31c36559a093672e83c296`

**Security warning:** The EXE contains an embedded license key. Base64 is not encryption. The key can be extracted by anyone with access to this public branch or executable.

Full Windows application behavior has not been tested.
