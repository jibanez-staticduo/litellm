# Stable Promotion

- Initial stable state: unresolved/not found
- Approved source: `docker.staticduo.com/litellm@sha256:35fc520902eb72f5ea91ececccf221883dd5fd78b1d47c78150dfd66eb04f2d3`
- Initial Buildx default result: manifest list `sha256:457e528cb968e5a7c5e9892a5935129b13a8d091b57c6290ea6ac1b5dc74f7e2` with the approved manifest as its sole `linux/amd64` child
- Corrective direct promotion: locally tag the already digest-pinned approved image as `docker.staticduo.com/litellm:stable`, then `docker push docker.staticduo.com/litellm:stable`
- Final push result: `stable: digest: sha256:35fc520902eb72f5ea91ececccf221883dd5fd78b1d47c78150dfd66eb04f2d3 size: 4723`
- No host container, service, database, model, route, credential, dependency, or source file was changed by promotion
