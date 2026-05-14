FROM mcr.microsoft.com/devcontainers/python:1-3.12-bookworm

# Workaround: remove stale Yarn APT source that can break feature installation.
RUN rm -f /etc/apt/sources.list.d/yarn.list \
    /etc/apt/sources.list.d/yarn.list.save \
    /etc/apt/sources.list.d/yarn.sources \
    /usr/share/keyrings/yarnkey.gpg
