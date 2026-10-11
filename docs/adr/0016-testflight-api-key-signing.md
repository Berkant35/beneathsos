# 0016. iOS signing and TestFlight with an App Store Connect API key

- Status: Accepted
- Date: 2026-10-11

## Context

The first release build with the new bundle id `org.beneathsos.app` archived fine but failed to
export: Xcode's Apple ID session had expired, so it could not create an App Store provisioning
profile. Depending on a logged-in Xcode makes releases fragile and impossible to automate in CI.

## Decision

`tools/testflight.sh` in the app repository:

1. `flutter build ios --config-only` with the build number = **git commit count**;
2. `xcodebuild archive` and `xcodebuild -exportArchive` with `-allowProvisioningUpdates` and the
   App Store Connect API key (`-authenticationKeyPath/-ID/-IssuerID`), using `ios/ExportOptions.plist`
   (`app-store-connect`, automatic signing);
3. `xcrun altool --upload-app` with the same key.

The key lives in `~/.private_keys/` and is never committed; key id and issuer come from environment
variables. `ITSAppUsesNonExemptEncryption = false` skips the export-compliance question.

## Alternatives

- **Log in to Xcode** — works on one machine, not in CI, and expires.
- **fastlane match** — robust, but needs a separate encrypted certificate repository.
- **Xcode Cloud** — tied to Apple's CI and its own configuration.

## Consequences

- Verified: Xcode created the App Store profile through the key; the IPA is signed with Apple
  Distribution; builds 0.1.0 (4) and (6) were processed by Apple in about two minutes.
- The key needs the Admin or App Manager role.
- The same script can run in GitHub Actions once the maintainer stores the key as a repository
  secret.
- Build numbers skip values when commits are not uploaded; they always increase.

## References

- `apps/beneathsos_app/tools/testflight.sh`, `ios/ExportOptions.plist`, app README.
