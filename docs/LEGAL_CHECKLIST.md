# Legal and Release Checklist

This checklist is for preparing a public GitHub release.

## Before Publishing

- Keep `LICENSE` in the repository root for this project's own code.
- Keep `THIRD_PARTY_NOTICES.md` and `licenses/PyAutoGUI-LICENSE.txt`.
- Mention that this project depends on or builds around PyAutoGUI, but do not state or imply official affiliation.
- Do not copy PyAutoGUI documentation, logos, screenshots, or README sections unless the license terms are checked and attribution is preserved.
- Do not remove safety notes about user authorization, platform terms, verification/captcha boundaries, or anti-spam behavior.
- If any upstream PyAutoGUI source file is copied into this repository later, preserve its original copyright/license notice and document what changed.

## Suggested GitHub Repository Description

```text
CLI-Anything PyAutoGUI harness plus a Codex skill for user-authorized Boss Zhipin job application automation. Unofficial; depends on PyAutoGUI.
```

## Suggested README Disclaimer

```text
This is an unofficial project. It is not affiliated with, sponsored by, or endorsed by PyAutoGUI, Al Sweigart, Boss Zhipin, or their contributors/owners.
```

## Practical Boundaries

- Use the tool only on accounts and desktop sessions you are authorized to operate.
- Respect website terms and platform rate limits.
- Do not bypass captcha, phone verification, QR login, anti-bot checks, or access controls.
- Do not use the project for spam, impersonation, credential collection, or unauthorized data extraction.
