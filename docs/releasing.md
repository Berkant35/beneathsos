# Releasing BeneathSOS v1 (maintainer checklist)

Everything that can be prepared in the repositories is done; the steps below need the maintainer's
accounts, signing material or a decision, so they stay manual.

## iOS — App Store
1. TestFlight: `apps/beneathsos_app/tools/testflight.sh` (build number = commit count). Try every flow on
   a phone: a search end to end, "I am trapped" on a second phone, export, record found.
2. App Store Connect → app 6821632633:
   - Version 1.0.0, texts from [`store/listing.md`](store/listing.md) (EN + TR), screenshots (6.9" and
     6.5" iPhone; simulator `xcrun simctl io booted screenshot`), category Utilities.
   - App Privacy: **Data Not Collected**; privacy policy URL [`privacy.md`](privacy.md) on GitHub.
   - Age rating: none of the content questions apply.
   - Export compliance: `ITSAppUsesNonExemptEncryption = NO` is already in `Info.plist`.
   - Review notes: see the listing.
3. Submit for review, then release manually.

## Android — Google Play
1. Create the upload key once (never commit it):
   `keytool -genkey -v -keystore ~/.private_keys/beneathsos-upload.jks -keyalg RSA -keysize 2048 -validity 10000 -alias upload`
2. `apps/beneathsos_app/android/key.properties` (git-ignored):
   `storeFile=/Users/<you>/.private_keys/beneathsos-upload.jks`, `storePassword=…`, `keyAlias=upload`,
   `keyPassword=…`.
3. `fvm flutter build appbundle --release` → upload to Play Console (internal testing first). Data safety:
   no data collected or shared. Permissions: Bluetooth scan / advertise, location (Android requires it
   for Bluetooth scanning; never used for position).

## Repositories
- Tag the app `v1.0.0` once the store build is approved; CHANGELOG from Conventional Commits.
- Packages are already tagged (`rubble_core` v0.2.0, `locator_engine` v0.1.1, `ble_scanner` v0.2.1,
  `rubble_canvas` v0.4.0, `beneathsos_ui` v0.3.1).

## Known limits of v1 (say them in the release notes)
- iOS victim mode advertises only while the app is open or recently backgrounded; Android stops when the
  app is closed (no foreground service yet).
- Engine profiles are from simulation; field calibration is the next research step (export + record
  found exist for that).
