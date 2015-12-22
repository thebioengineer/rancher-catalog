FROM rancher/dind:v0.6.0

ADD ./scripts/bootstrapAxio /scripts/bootstrapAxio
RUN /scripts/bootstrapAxio
