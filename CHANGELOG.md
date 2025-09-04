# Changelog

## [0.1.9](https://github.com/terraharbor/backend/compare/v0.1.8...v0.1.9) (2025-09-04)


### Features

* implemented lock ID check ([2de6001](https://github.com/terraharbor/backend/commit/2de60011ac262f6eb128d8e4978a929825e66b48))
* implemented lock ID check ([255f09b](https://github.com/terraharbor/backend/commit/255f09bb2527257e0e198c94079b505e316353a6))
* use backend to test Terraform ([2792bfd](https://github.com/terraharbor/backend/commit/2792bfd64b365bb50cb6d1aab8c92bcc3edd7947))


### Bug Fixes

* disable commit of .terraform folders ([c4c3cda](https://github.com/terraharbor/backend/commit/c4c3cdad30925a833dc8418b3dbede63ac9a21a0))


### Miscellaneous Chores

* commit the .env file ([59b5e75](https://github.com/terraharbor/backend/commit/59b5e75c61ac2dffa72a7e4956bd239fcc86df7c))
* Merge main into feat/lock_id_verification ([0cde3ad](https://github.com/terraharbor/backend/commit/0cde3ad4cfd3df8cbde26dadd3406a3cfa52d916))
* merge pull request [#53](https://github.com/terraharbor/backend/issues/53) from terraharbor/tests/terraform-test ([b688d61](https://github.com/terraharbor/backend/commit/b688d619908b819d615e341c98ce8d284a7ad7dd))
* merge pull request [#66](https://github.com/terraharbor/backend/issues/66) from terraharbor/feat/lock_id_verification ([2de6001](https://github.com/terraharbor/backend/commit/2de60011ac262f6eb128d8e4978a929825e66b48))


### Code Refactoring

* remove debug output ([6dae743](https://github.com/terraharbor/backend/commit/6dae7435dd37dfc690f3a956f3be3399b1eac6e4))


### Tests

* add beginning of tests ([2869daf](https://github.com/terraharbor/backend/commit/2869dafd7db43c01bef6694c918ce3099749e1e5))


### Continuous Integration

* add Terraform steps ([321d8f9](https://github.com/terraharbor/backend/commit/321d8f975fb9eb3e9c55f8ecdfd13076fa31b8e3))
* add test with steps that start the docker compose ([7c4bccd](https://github.com/terraharbor/backend/commit/7c4bccdd43edf8ff71a1565510a9f481375b85af))

## [0.1.8](https://github.com/terraharbor/backend/compare/v0.1.7...v0.1.8) (2025-09-03)


### Features

* Implement compatibility with basic auth ([86062b6](https://github.com/terraharbor/backend/commit/86062b64bd07f2b294b88ed47792f97b694a6959))


### Bug Fixes

* fix for custom methods ([7ac7bc2](https://github.com/terraharbor/backend/commit/7ac7bc29e268daf29d360dc2696685ed1a8a8ccc))
* fix for custom methods ([d363294](https://github.com/terraharbor/backend/commit/d3632947f1e59ab9107a07b28260f837c5918fc3))
* Implemented custom dependency to handle basic and bearers ([12789e9](https://github.com/terraharbor/backend/commit/12789e9bb5e2e8ea969a9ea79ffadef3c9ec3f07))
* trying to fix ([0b67cf9](https://github.com/terraharbor/backend/commit/0b67cf91e4aa292fc733ae71cfefe65fc6a028fa))
* typo ([a038e95](https://github.com/terraharbor/backend/commit/a038e95e16f38703651b02686af174a26b91fee4))
* use `/health` instead of `/health_check` and add `curl` ([d01e13a](https://github.com/terraharbor/backend/commit/d01e13a861285d861a833f3974bb80bc738bb219))
* use `/health` instead of `/health_check` and add `curl` ([a028cb4](https://github.com/terraharbor/backend/commit/a028cb4cf4e83e192b7f069168d46eb6d8d21d6e))


### Styles

* made a separate file for the dependancy ([8a3380a](https://github.com/terraharbor/backend/commit/8a3380a753be04974c3b702438aeb3a2d821509a))
* made a separate file for the dependancy ([b0f8d85](https://github.com/terraharbor/backend/commit/b0f8d8510402f1f9947e53be315cf1cc50f00d28))


### Miscellaneous Chores

* Merge main into feat/basic_auth ([bc61e68](https://github.com/terraharbor/backend/commit/bc61e687c66b4071229178c88e43e8e752f55599))
* Merge main into feat/basic_auth ([ceb01c1](https://github.com/terraharbor/backend/commit/ceb01c1ba63b9e6ba7f9c7a48696427a1cd90dc0))
* Merge pull request [#50](https://github.com/terraharbor/backend/issues/50) from terraharbor/fix/health ([d01e13a](https://github.com/terraharbor/backend/commit/d01e13a861285d861a833f3974bb80bc738bb219))
* Merge pull request [#62](https://github.com/terraharbor/backend/issues/62) from terraharbor/fix/lock-unlock-compat ([7ac7bc2](https://github.com/terraharbor/backend/commit/7ac7bc29e268daf29d360dc2696685ed1a8a8ccc))

## [0.1.7](https://github.com/terraharbor/backend/compare/v0.1.6...v0.1.7) (2025-09-02)


### Features

* health check endpoint added ([616766d](https://github.com/terraharbor/backend/commit/616766d5c4637105d85b9b63fe9bcc3745f8b8ab))
* health check endpoint added ([c97cef0](https://github.com/terraharbor/backend/commit/c97cef0eb93acad787da6649f23b5c99b6b1a2bc))


### Bug Fixes

* fix frontend compatibility ([ea146a5](https://github.com/terraharbor/backend/commit/ea146a56a3fa32d57b3802354a20dba4f95d2458))
* fix frontend compatibility ([3780e74](https://github.com/terraharbor/backend/commit/3780e74361dd7b02d7b647e776e4cfa511c06a33))
* fixed /token when user does not exist ([df3984a](https://github.com/terraharbor/backend/commit/df3984a621658d3f43ca66e19f29aaacf4ec400b))
* fixed /token when user does not exist ([8397af4](https://github.com/terraharbor/backend/commit/8397af4b150e972d5d3e4474f988370449f2dfa2))
* merge pull request [#44](https://github.com/terraharbor/backend/issues/44) from terraharbor/fix/token_endpoint ([df3984a](https://github.com/terraharbor/backend/commit/df3984a621658d3f43ca66e19f29aaacf4ec400b))


### Miscellaneous Chores

* Merge from terraharbor/feat/health_check ([616766d](https://github.com/terraharbor/backend/commit/616766d5c4637105d85b9b63fe9bcc3745f8b8ab))
* Merge main into fix/token_endpoint ([1222165](https://github.com/terraharbor/backend/commit/12221653b9ac35272f2999ed491bcbc12a00491d))

## [0.1.6](https://github.com/terraharbor/backend/compare/v0.1.5...v0.1.6) (2025-09-01)


### Features

* create separate role and evolutive scripts ([c98508c](https://github.com/terraharbor/backend/commit/c98508cba1776891b51b2a09b96203d219789b8c))


### Bug Fixes

* added lacking column ([dc6ffcd](https://github.com/terraharbor/backend/commit/dc6ffcd818d3b02079bbc575bdd9a9da0dab2bb4))
* remove old init script ([a540eea](https://github.com/terraharbor/backend/commit/a540eeaead742ca56f8536c4da9707b37c41d1fb))


### Miscellaneous Chores

* merge pull request [#40](https://github.com/terraharbor/backend/issues/40) from terraharbor/feat/database-creation ([af4eaea](https://github.com/terraharbor/backend/commit/af4eaea2adf64477ed5a8b33a4ca5a12d7e4e2ae))

## [0.1.5](https://github.com/terraharbor/backend/compare/v0.1.4...v0.1.5) (2025-08-31)


### Features

* Enhanced logging ([2690a59](https://github.com/terraharbor/backend/commit/2690a599a37181a780b3aceabe447a5f05ee85fb))
* Implemented state versioning & deletion ([e3794ed](https://github.com/terraharbor/backend/commit/e3794edff3f80fb50e883e2d0218b10e5164e32b))
* states versioning & deletion ([118bcf6](https://github.com/terraharbor/backend/commit/118bcf6876b04ce1ff803e977de4b57201c7adba))


### Bug Fixes

* Fixed work space ([0c470e5](https://github.com/terraharbor/backend/commit/0c470e5bfa433a0716030452bce61e79262f60e1))


### Documentation

* updated endpoint docs ([9e5d5b7](https://github.com/terraharbor/backend/commit/9e5d5b74a2701ae3fd32ece2f9fe56eedcd298ba))


### Miscellaneous Chores

* Merge branch 'main' into refactor/salt_passwords ([ae52fac](https://github.com/terraharbor/backend/commit/ae52fac4dc3b25454d3de805d125eeab7d8c2a21))


### Code Refactoring

* Implemented password salting ([c9de3a4](https://github.com/terraharbor/backend/commit/c9de3a484a6c43f1cac81cb80eea728de59f52f9))
* password security upgrade ([f1cae81](https://github.com/terraharbor/backend/commit/f1cae818589956c9def704ca5ef726a486a6905a))


### Build System

* Removed intruction repeated twice uselessly ([656ebb0](https://github.com/terraharbor/backend/commit/656ebb01f9197271fdd52604be8530da5f4cde10))

## [0.1.4](https://github.com/terraharbor/backend/compare/v0.1.3...v0.1.4) (2025-08-27)


### Features

* implement api endpoints ([d6362ff](https://github.com/terraharbor/backend/commit/d6362ff41f8dae43a4de895c16c3657ef5f195ad))


### Bug Fixes

* fixed conflicts ([1d2c150](https://github.com/terraharbor/backend/commit/1d2c1507be5acd07568df344c5a81279f3e50a4d))


### Miscellaneous Chores

* **deps:** pin python docker tag to 9ba6d8c ([64fbe8b](https://github.com/terraharbor/backend/commit/64fbe8bf5826ec3ff0c467603c4d3bb9fa4104f5))
* **deps:** pin python docker tag to 9ba6d8c ([64fbe8b](https://github.com/terraharbor/backend/commit/64fbe8bf5826ec3ff0c467603c4d3bb9fa4104f5))
* **deps:** pin python docker tag to 9ba6d8c ([2dcf41f](https://github.com/terraharbor/backend/commit/2dcf41f22b57b542401c3275f88baaa085faf575))

## [0.1.3](https://github.com/terraharbor/backend/compare/v0.1.2...v0.1.3) (2025-08-26)


### Features

* **backend:** moved backend files ([72c8969](https://github.com/terraharbor/backend/commit/72c8969e5670927454f94543ec1f8bc080cb18d3))
* **backend:** moved backend files ([97f4a9d](https://github.com/terraharbor/backend/commit/97f4a9db2cfdd01a825827f3dfc12072d1c81bee))

## [0.1.2](https://github.com/terraharbor/backend/compare/v0.1.1...v0.1.2) (2025-07-24)


### Miscellaneous Chores

* **deps:** update traefik/whoami docker tag to v1.11.0 ([#6](https://github.com/terraharbor/backend/issues/6)) ([8488651](https://github.com/terraharbor/backend/commit/84886513e06e891fec20b7f0db191da828970343))

## [0.1.1](https://github.com/terraharbor/backend/compare/v0.1.0...v0.1.1) (2025-07-24)


### Miscellaneous Chores

* trigger release ([cc953e3](https://github.com/terraharbor/backend/commit/cc953e36d93dc91f88a0c252591e3b82625252af))


### Continuous Integration

* add/edit docker-build.yaml ([adcd08d](https://github.com/terraharbor/backend/commit/adcd08da695846ff1d911d0b48a5dd224ef59f6d))

## 0.1.0 (2025-07-24)


### Features

* add simple Dockerfile ([bb399b8](https://github.com/terraharbor/backend/commit/bb399b8af1ead9999eed95f42dd92ad2e2d2d7a4))
* add simple Dockerfile ([25618ff](https://github.com/terraharbor/backend/commit/25618ff64cd64bd14ad5d235f363bf1334b129d3))


### Miscellaneous Chores

* add/edit .renovaterc.json ([746d515](https://github.com/terraharbor/backend/commit/746d5154ecc602c6bef8c7f2a26c4596d81fad20))
* add/edit CODEOWNERS ([717ffed](https://github.com/terraharbor/backend/commit/717ffed2e4b4f85270fd7ea17cd0570d6f1c711d))
* add/edit LICENSE.txt ([e33132c](https://github.com/terraharbor/backend/commit/e33132c50159b7ce61b5fa089c883a6847e1589d))
* add/edit release-please-config.json ([86e9517](https://github.com/terraharbor/backend/commit/86e95177c3e10b628f9cc149bf4519125f41dd4a))
* add/edit release-please-manifest.json ([88aa454](https://github.com/terraharbor/backend/commit/88aa454e6900427c58fa2661a19b8c9972ffba4d))
* merge pull request [#4](https://github.com/terraharbor/backend/issues/4) from terraharbor/feat/add-dockerfile ([bb399b8](https://github.com/terraharbor/backend/commit/bb399b8af1ead9999eed95f42dd92ad2e2d2d7a4))
* trigger release ([f950e51](https://github.com/terraharbor/backend/commit/f950e51c4eed989d1be5bf1e31b471abd8025c77))


### Continuous Integration

* add/edit commits-checks.yaml ([724b976](https://github.com/terraharbor/backend/commit/724b97680cc38fc96760231de3873f222ce64396))
* add/edit docker-build.yaml ([9f99f82](https://github.com/terraharbor/backend/commit/9f99f8207316169dc5cb3b9eee888fa498f05791))
* add/edit docker-build.yaml ([8da6d14](https://github.com/terraharbor/backend/commit/8da6d14bf0a146e6dbed92349e9fc9bc1d8201e8))
* add/edit docker-build.yaml ([51c7188](https://github.com/terraharbor/backend/commit/51c718866b7b9416ca22dec563bc426d94d849ce))
* add/edit docker-build.yaml ([22d20d6](https://github.com/terraharbor/backend/commit/22d20d63f5f386b265b50b9bd30b16160cc302f9))
* add/edit pr-issues-project.yaml ([d94ce6c](https://github.com/terraharbor/backend/commit/d94ce6ca7dce0cf9cb99e7a58feff00a10f0e0d0))
* add/edit release-please.yaml ([6311593](https://github.com/terraharbor/backend/commit/63115932abb3186919ce8c93129eae286b0589db))
