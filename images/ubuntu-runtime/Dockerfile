FROM curlimages/curl AS chisel
USER 0
ARG CHISEL_VERSION
ARG UBUNTU_VERSION
RUN if [[ "$(arch)" == "x86_64" ]]; then \
        architecture="amd64"; \
    else \
        architecture="arm64"; \
    fi; \
    curl -L https://github.com/canonical/chisel/releases/download/${CHISEL_VERSION}/chisel_${CHISEL_VERSION}_linux_${architecture}.tar.gz \
      -o chisel.tar.gz \
    && tar -xvzf chisel.tar.gz \
    && mv chisel /usr/local/bin
WORKDIR /staging
RUN chisel cut \
      --release ubuntu-${UBUNTU_VERSION} \
      --root ./ \
      base-files_base \
      base-files_copyright \
      base-passwd_data \
      base-files_release-info \
      busybox_bins \
      busybox_copyright \
      ca-certificates_bins \
      ca-certificates_copyright \
      ca-certificates_data-with-certs \
      libc6_copyright \
      libc6_libs \
      tzdata_zoneinfo \
      tzdata_copyright

FROM scratch
COPY --from=chisel /staging /
RUN ["/bin/busybox", "--install"]
USER 1000
