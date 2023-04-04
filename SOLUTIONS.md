## Challenge 1 - The API returns a list instead of an object
---
To solve this, I made the following changes:

- Imported the `abort` function from Flask.
- Modified the `find_restaurants` function to handle cases where `_id` is not provided. If `_id` is provided, it tries to find a restaurant with that ID in the database using a more specific function `mongo.db.restaurant.find_one()`. If no restaurant is found, it returns a tuple containing an error message and a status code of 204. If `_id` is not provided, it retrieves all restaurants from the database using `mongo.db.restaurant.find()`.
- Removed the `query` variable that was previously used to construct the query for finding restaurants by ID.

## Challange 2 - Test the application in any cicd system
---
I chose to use GitHub Actions as it allows for easy creation and execution of workflows directly from the repository. However, I must note that this may not be the best option for this infrastructure as the workflow is executed outside the cluster. This means that access needs to be provided from GitHub to the cluster in order to deploy Kubernetes resources or access the database. In such cases, internal CI/CD tools like Jenkins or GitLab, deployed inside the cluster, are recommended. Unfortunately, due to low machine resources and issues with agent/runner configuration, I was unable to set up these tools.

File: `.github/workflows/main.yml`

**The workflow steps I have implemented so far include:**
- Checking out the code
- Building the image
- Pushing the image to the registry
- Updating the image version in manifests

**However, there are two steps that are yet to be completed:**
- The test step cannot be performed as it requires deploying a MongoDB instance and using the test database.
- The apply manifest step cannot be performed as GitHub does not have access to my local cluster. This would need to be clarified and resolved.

Overall, while GitHub Actions may not be the ideal choice for this particular infrastructure, it can still be used effectively for simpler projects.

## Challenge 3 - Dockerize the APP
---
The challenge here is to build the smallest possible image using a Dockerfile.

To accomplish this, I have created a simple `Dockerfile` that retrieves the dependencies and runs the `python app.py` command. While this may seem straightforward, it is important to ensure that the Dockerfile is optimized for size and efficiency.

For simplicity, I have used DockerHub as my container registry. However, it is worth noting that I only have one repository available to push to. In a real-world scenario, you would likely need to use a more robust container registry solution that allows for multiple repositories and advanced features such as access control and vulnerability scanning.

The Dockerfile first creates a build stage with the necessary dependencies and then copies them into the final image. It also sets the environment variable path to include the local bin directory. This ensures that the application can be run without any issues.

To build the Docker image:

```
docker build -t <registry_username>/<app_name>:<app_version> .
```

To run it locally:

```bash
docker run --rm -it --name $APP_NAME\
-p $APP_PORT:$APP_PORT \
-e MONGO_URI="mongodb://$MONGO_INITDB_ROOT_USERNAME:$MONGO_INITDB_ROOT_PASSWORD@localhost:$MONGO_DB_PORT/$MONGO_DB_DATABASE"
<registry_username>/<app_name>:<app_version>
```

## Challenge 4 - Dockerize the database
---
For the database, I run the official mongo image. It receives the minimum variables to start:

```bash
docker run --rm -it --name mongodb \
-p $MONGO_DB_PORT:$MONGO_DB_PORT \
-e MONGO_INITDB_ROOT_USERNAME=$MONGO_INITDB_ROOT_USERNAME \
-e MONGO_INITDB_ROOT_PASSWORD=$MONGO_INITDB_ROOT_PASSWORD \
-d mongo
```

To populate the database with the restaurant.json file:

```bash
mongoimport \
-h localhost \
-p $MONGO_DB_PORT \
-d $MONGO_DB_DATABASE \
-c $MONGO_DB_COLLECTION \
-u $MONGO_INITDB_ROOT_USERNAME \
-p $MONGO_INITDB_ROOT_PASSWORD \
--file data/restaurant.json
```

## Challange 5 - Docker Compose it
---
For this challange, I've created a `docker-compose` file that deploys both the app and database.

The docker-compose creates two services. The app service that builds the Docker image from the current directory and sets the environment variable for the MongoDB URI as the connection string. It also maps the container port to the host port and depends on the MongoDB service.

The MongoDB service uses the official MongoDB image and sets the environment variables for the `root` username and password. It also maps the container port to the host port and mounts the volume for the MongoDB data directory. Additionally, it starts the db with `mongod` command with authentication and imports the restaurant data from the restaurant.json file.

## Challenge 6 - Deploy it on kubernetes
---
I have created a Kubernetes cluster using Rancher Desktop and created the namespace `project`. To deploy MongoDB, I used the Bitnami Mongo Helm chart as it creates all the necessary Kubernetes resources.

### Obtaining the password

To obtain the `mongodb` password, use the following command:

```bash
kubectl get secret --namespace project mongodb -o jsonpath="{.data.mongodb-root-password}" | base64 -d"
```

### Creating the MONGO_URI variable

The internal host for `mongodb` is `mongodb.project.svc.cluster.local`. This should be used to create the `MONGO_URI` variable. For simplicity, I set a secret in the cluster with the string:

```bash
MONGO_URI=mongodb://$MONGO_INITDB_ROOT_USERNAME:$MONGO_INITDB_ROOT_PASSWORD@mongodb.project.svc.cluster.local:$MONGO_DB_PORT/$MONGO_DB_DATABASE
```

### Creating a database and collection

To create the database and collection, you can use the command:

```bash
mongoimport -h mongodb.project.svc.cluster.local -p $MONGO_DB_PORT -d $MONGO_DB_DATABASE -c restaurant -u $MONGO_INITDB_ROOT_USERNAME -p $MONGO_INITDB_ROOT_PASSWORD --file data/restaurant.json"
```

### Manual steps

For this challenge, I had to create some components manually as they couldn't be applied in the CI/CD pipeline due to being on different networks. These steps include:

- Creating a secret for Dockerhub credentials
- A secret with Mongo URI string.
- Port-forwarding of services. Alternatively, you could resolve this by placing an ingress in front of the app service.

## Final Thoughts and Conclusion
---
### Security Improvements
One area that needs improvement is security. Specifically, we need a way to manage credentials securely. One suggestion would be to use Kubernetes secrets to store sensitive information such as passwords and API keys. Additionally, we should consider implementing RBAC (Role-Based Access Control) to restrict access to resources based on user roles.

### Using ArgoCD for Synchronization
Another suggestion would be to use ArgoCD to synchronize the repository changes into Kubernetes resources. This would allow for easier management of deployments and updates, as well as provide a more streamlined workflow for developers.

### Database Security
Regarding database security, creating a new non-root user to use instead of the root user would be a good practice. This would limit the potential damage that could be done if the root user's credentials were compromised.

### Deployment Improvements
Finally, there are some improvements that could be made to the deployment process. For example, adding readiness and liveness probes to the application would ensure that it is running correctly and can handle requests. Additionally, using a more robust container registry solution with advanced features such as access control and vulnerability scanning would be beneficial.

In conclusion, this challenge was a great learning experience, there are still areas that could be improved to ensure better security, efficiency, and ease of management.