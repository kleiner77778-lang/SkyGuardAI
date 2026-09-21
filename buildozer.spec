Name: Build Android APK

on:
  push:
    branches: [ main, master ]
  workflow_dispatch:

jobs:
  build:
    runs-on: ubuntu-22.04

    steps:
      - name: Checkout Code
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.10'

      - name: Set up Java 17
        uses: actions/setup-java@v4
        with:
          distribution: 'temurin'
          java-version: '17'

      - name: Install System Dependencies
        run: |
          sudo apt-get update
          sudo apt-get install -y \
            build-essential \
            ccache \
            git \
            libffi-dev \
            libssl-dev \
            libltdl-dev \
            zip \
            unzip \
            openjdk-17-jdk
          pip install --upgrade pip
          pip install "cython==0.29.33" buildozer
      - name: Build APK with Buildozer
        run: |
          # Automatisiertes Bestätigen aller Lizenzen beim ersten Start
          yes | buildozer android debug
      - name: Upload APK Artifact
        uses: actions/upload-artifact@v4
        with:
          name: package-apk
          path: bin/*.apk
          if-no-files-found: error
