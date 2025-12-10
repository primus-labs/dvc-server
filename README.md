# dvc-server


## Overview

This project is a simple and secure service designed to run inside a **Trusted Execution Environment (TEE)**. Its primary purpose is to run a **zkVM prover**, process incoming proof requests, and return verified proof results in a confidential and tamper-resistant environment.

The service supports:

* Configurable proving backends (`mock`, `cpu`, `cuda`, `network`)
* Optional HTTPS with certificate-based SSL/TLS
* Runtime configuration through a simple `.env` file
* Easy startup via a Python HTTPS/HTTP server


## Usage

1. Create a `.env` file in the project root.
2. Copy the configuration template (see the **[Configuration Guide](#configuration-guide)** below).
3. Update the configuration values as needed (port, SSL settings, prover mode, etc.).
4. Replace the prover binary in the `bin/` directory with your own build generated via
   [DVC-Succinct](https://github.com/primus-labs/DVC-Succinct), if applicable.
5. Start the service:

    ```bash
    python https_server.py
    ```
    
    The server will automatically read all settings from `.env`.



## Configuration Guide

This project uses a `.env` file to configure server behavior, SSL/TLS parameters, and zkVM proving settings.

Below is a description of each configuration and how to use them.


### 1. Server Configuration

#### **PORT**

The TCP port that the service will listen on.

* Default: `8080`
* Example:

    ```
    PORT=8000
    ```


### 2. SSL/TLS Configuration

These options control whether the service runs with HTTPS.

#### **USE_SSL**

Enables or disables SSL/TLS.

* `ON` — enable HTTPS
* `OFF` — disable HTTPS (default)
* If not set, the service defaults to `OFF`.

    ```
    USE_SSL=OFF
    ```

#### **CERTFILE**

Path to the SSL certificate file (`.crt` or `.pem`).

* Required **only when `USE_SSL=ON`**
* Example:

    ```
    CERTFILE=./certs/server.crt
    ```

#### **KEYFILE**

Path to the private key associated with the certificate.

* Required **only when `USE_SSL=ON`**
* Example:

    ```
    KEYFILE=./certs/server.key
    ```

If SSL is disabled, both fields may remain empty.


### 3. zkVM Configuration

These settings configure the proving mode used by the zkVM.

#### **SP1_PROVER**

Specifies which prover backend to use.

Available options:

* `mock` — generate mock proofs locally
* `cpu` — generate real proofs on CPU
* `cuda` — generate real proofs on GPU
* `network` — use the Succinct Prover Network

Example:

```
SP1_PROVER=cpu
```

#### **NETWORK_PRIVATE_KEY**

Required **only when `SP1_PROVER=network`**.

This is the private key used to authenticate with the Succinct Prover Network.
You can set up an account [here](https://docs.succinct.xyz/docs/sp1/prover-network/quickstart).

```
NETWORK_PRIVATE_KEY=
```
