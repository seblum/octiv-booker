### Chromedriver Version

The current Chromedriver version is not fixed and needs to be fetched from an external source.

To fetch the last stable version programmatically, use the following JSON endpoint:

- [Fetch Last Stable Version JSON](https://googlechromelabs.github.io/chrome-for-testing/last-known-good-versions.json)

Alternatively, you can manually check the latest stable version here:

- [Google Chrome Labs - Stable Versions](https://googlechromelabs.github.io/chrome-for-testing/#stable)


```yaml
config.yaml
# TODO: Comment fully for local development
# Use second for docker image
# chromedriver: '/usr/local/bin/chromedriver'
# chromedriver: '/usr/local/bin/chromedriver-linux64/chromedriver'

base_url: 'https://app.octivfitness.com/login'
```
