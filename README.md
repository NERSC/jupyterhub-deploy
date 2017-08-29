# NERSC JupyterHub Deployment

There are three Dockerfiles.

## Base Dockerfile

This is the common frame of reference for our JupyterHub installation.
While we are developing we can create this Docker image and from new images off of it for various purposes.
The base image comes from Ubuntu:16.04 and installs the NERSC fork of JupyterHub and that is about it.
If you find you need to `apt-get install` packages in derived images, think about putting them here.

JupyterHub should always come from a specific tag of our fork.
Would be nice to make it easy to adjust that.

## Dockerfile for jupyter.nersc.gov

This Dockerfile builds the setup for a Docker-based JupyterHub + Jupyter installation.
Basically the science gateway deployment right now.

## Dockerfile for jupyter-dev.nersc.gov

Dockerfile and supporting files (currently certs) for the cori login node deployment of JupyterHub.

    BASE_PATH    The path to the python install on the remote system
    ADMINS       A comma seperated list of admin usernames
    SSL_KEY      Path to the SSL key (if SSL should be enabled).
    SSL_CERT     Path to the SSL cert  (if SSL should be enabled).
    REMOTE_HOST  Host:Port of the GSI SSH running on the remote system
    HUB_API_URL  URL of the HUB API (e.g. http://jupyter-dev.nersc.gov:8082/hub/api)

Probably the authenticator and SSH spawner should come from a specific tag on each repo.

## Additional setups

Other directories can be added for various testing.

## Future Work

Eventually the two derived image builds should merge into one using WrapSpawner.
This would provide a single point of entry for Jupyter at NERSC for:

* Jupyter in Spin (hub separate from notebooks and kernels though).
* Jupyter on Cori19
* Jupyter on Cori computes via reservation, interactive queue, etc.

## Scripts

These are management scripts.
