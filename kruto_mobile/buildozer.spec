
[app]
title = kruto_mob
package.name = kruto_mob
package.domain = org.kruto.mob
source.dir = mobile
source.include_exts = py,png,jpg,kv,atlas,db
version = 1.0
icon.filename = %(source.dir)s/kruto.png

# (str) Supported orientation (one of: landscape, sensorLandscape, portrait or all)
orientation = portrait

# (list) Permissions
android.permissions = INTERNET

# (str) Presplash of the application
# presplash.filename = %(source.dir)s/data/presplash.png

# (list) Supported platforms
# android.archs = armeabi-v7a, arm64-v8a

# (str) Application entry point
entrypoint = mob4.py

# (str) Android NDK version to use
android.ndk = 23b

# (str) Android SDK version to use
android.api = 33

# (str) Python version to use
python.version = 3

# (list) Application requirements
requirements = python3,kivy

# (str) Custom source folders for requirements
# (Separate multiple paths with commas)
# requirements.source =

[buildozer]
log_level = 2
warn_on_root = 1
