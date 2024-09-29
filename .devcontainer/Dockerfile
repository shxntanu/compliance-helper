FROM mcr.microsoft.com/devcontainers/python:0-3.11

# Install additional OS packages
RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
    && apt-get -y install --no-install-recommends \
    bash-completion \
    vim

# Create a non-root user to use if preferred - see https://aka.ms/vscode-remote/containers/non-root-user.
ARG USERNAME=vscode
ARG USER_UID=1000
ARG USER_GID=$USER_UID

# [Optional] Set the default user. Omit if you want to keep the default as root.
USER $USERNAME

# Set up the virtual environment
ENV VIRTUAL_ENV=/workspaces/${workspaceFolderBasename}/.venv
RUN python -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Install pip requirements (if any)
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# [Optional] Uncomment this section to install additional OS packages.
# USER root
# RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
#     && apt-get -y install --no-install-recommends <your-package-list-here>
# USER $USERNAME