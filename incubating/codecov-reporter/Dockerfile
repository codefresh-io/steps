# syntax=docker/dockerfile:1

FROM --platform=${BUILDPLATFORM} alpine:3.24.4@sha256:f59abe656b692d901e184be3445e084786602108599d2a51d229c0f5a48c71bf AS build
ARG CF_CLI_VERSION=v1.3.6
ARG CODECOV_VERSION=v0.8.0
ARG TARGETARCH
WORKDIR /download
RUN apk add --no-cache curl gnupg
RUN case "${TARGETARCH}" in \
      amd64) CF_OS=alpine-x64; CODECOV_OS=alpine ;; \
      arm64) CF_OS=alpine-arm64; CODECOV_OS=aarch64 ;; \
      *) echo "unsupported architecture: ${TARGETARCH}" >&2; exit 1 ;; \
    esac \
    && curl -fsSL "https://github.com/codefresh-io/cli/releases/download/${CF_CLI_VERSION}/codefresh-${CF_CLI_VERSION}-${CF_OS}.tar.gz" \
      | tar -xz codefresh \
    && curl -fsSL https://keybase.io/codecovsecops/pgp_keys.asc \
      | gpg --dearmor > codecov.gpg \
    && curl -fsSLO "https://uploader.codecov.io/${CODECOV_VERSION}/${CODECOV_OS}/codecov" \
    && curl -fsSLO "https://uploader.codecov.io/${CODECOV_VERSION}/${CODECOV_OS}/codecov.SHA256SUM" \
    && curl -fsSLO "https://uploader.codecov.io/${CODECOV_VERSION}/${CODECOV_OS}/codecov.SHA256SUM.sig" \
    && gpgv --keyring ./codecov.gpg codecov.SHA256SUM.sig codecov.SHA256SUM \
    && sha256sum -c codecov.SHA256SUM \
    && chmod +x codefresh codecov


FROM alpine:3.24.4@sha256:f59abe656b692d901e184be3445e084786602108599d2a51d229c0f5a48c71bf
RUN apk add --no-cache git jq
COPY --from=build /download/codefresh /download/codecov /usr/local/bin/
RUN codefresh version && codecov --version
