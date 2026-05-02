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
      bash_bins \
      bash_copyright

FROM __hive_parent__
COPY --from=chisel /staging /
