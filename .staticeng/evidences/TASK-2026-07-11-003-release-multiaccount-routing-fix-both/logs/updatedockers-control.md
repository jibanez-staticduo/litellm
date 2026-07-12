# updatedockers control

The verified Compose parent was `/volume2/docker/updatedockers`. Its project name was `updatedockers`, its sole service/container was `updatedockers`, and it was running healthy before the maintenance window.

Only this project was stopped with `docker compose down`. Its container and project network were removed; no other Compose project was stopped. Local LiteLLM was then deployed from `/volume2/docker/litellm` and observed healthy on the target image for 30 seconds before `updatedockers` was restarted.

`docker compose up -d` recreated only the `updatedockers` project. The service returned to running/healthy. After a further 45-second observation, local LiteLLM remained running/healthy on the target routing-fix image.
