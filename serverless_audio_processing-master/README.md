# Serverless audio transcription with Python on IBM Cloud

This repository contains everything needed to deploy a serverless Python function for processing and transcribing audio at IBM Cloud.

## Requirements

### Tools

* IBM Cloud CLI (ibmcloud): https://cloud.ibm.com/docs/cli?topic=cli-install-ibmcloud-cli
* OpenWhisk plugin for IBM Cloud CLI (wsk): ```ibmcloud plugin install cloud-functions```
* [OPTIONAL] Docker (docker): https://hub.docker.com/?overlay=onboarding
* [OPTIONAL] cURL (curl)

### IBM Cloud services used

* Watson STT (speech-to-text): https://cloud.ibm.com/catalog/services/speech-to-text

## [OPTIONAL] building a custom Docker image for your serverless function

IBM Cloud Functions accepts any kind of Docker image as custom runtime for your functions, albeit you can only use images from public registries, such as an image that is publicly available on Docker Hub. Private registries are not supported.

In this example we will be using a custom Dockerfile with some Python libraries installed. This Docker image is publicly hosted on **vnderlev/custom-py-wsk:v5**, so building it is not required.

Nevertheless, to build an image and deploy it on Docker Hub you need to run the following commands:

login into Docker Hub

```
docker login -u <dockerhub_username> -p <dockerhub_password>
```

building a Docker image from a Dockerfile
```
docker build <dockerfile_directory> -t <dockerhub_username>/<repository_name>:<tag_name>
```

pushing a Docker image to Docker Hub
```
docker push <dockerhub_username>/<repo_name>:<tag_name>
```

## Managing Web actions with the IBM Cloud CLI

The IBM Cloud CLI plugin for working with OpenWhisk allow us to use "wsk" commands to create, deploy and debug any kind of serverless function into IBM Cloud. Below some useful commands are presented.

Deleting an existing Web action
```
ibmcloud wsk action delete <action_name>
```

Creating a raw Web action on IBM Cloud using a custom Dockerfile
```
ibmcloud wsk action create <action_name> --docker <dockerhub_username>/<image_name> <src_code_file> --web raw
```

Updating a raw Web action on IBM Cloud using a custom Dockerfile
```
ibmcloud wsk action update <action_name> --docker <dockerhub_username>/<image_name> <src_code_file> --web raw
```

Extracting the URL endpoint of the encapsulated serverless function
```
ibmcloud wsk action get <action_name> --url
```

Testing the deployed Web action with cURL
```
curl -F text=foo -F audio=@audio_sample.flac <action_url_endpoint>.json
```

Listing previous OpenWhisk activations
```
ibmcloud wsk activation list
```

You can get details about a specific activation record that resulted from an action invocation by running the following command. Replace <activation_id> with the id of the activation.

```
ibmcloud wsk activation get <activation_id>
```

Read more at: https://cloud.ibm.com/docs/openwhisk?topic=openwhisk-actions_web#actions_web_example
