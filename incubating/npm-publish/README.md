# Codefresh npm-publish Plugin

The release-to-npm can be used to publish images to npm. 

## Usage

Set required and optional environment variable and add the following step to your Codefresh pipeline:

```yaml
---
version: '1.0'

steps:

  ...

     deploy_to_npm:  
      title: Publishing To Npm 
      image: codefresh/npm-publish
      commands:
  ...

```

## Environment Variables

- **required** `NPM_TOKEN` - token of npm account

## How to use

- Add as a dependency to your project `npm install --save-dev publish-for-npm`

- Login into your project's NPM registry

```
npm login --registry <registry url>
npm login --registry http://registry.npmjs.org
```

- Copy the token

see how to extracting the NPM_TOKEN https://docs.npmjs.com/private-modules/ci-server-config#getting-an-authentication-token

- Set the token as environment variable

- Add script command

Create a script command to run the npm-publish, in your `package.json`

```json
{
    "scripts": {
        "npm-publish": "npm-publish"
    }
}
```




