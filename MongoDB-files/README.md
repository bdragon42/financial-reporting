## MongoDB and Kafka Deployments

---

This section details the the decision making behind the MongoDB and Kafka deployments for the project.
Although, I'm not going to be writing a "step-by-step", this sections also serves as a sort of "how-to" to anyone who might be interested.

For management of these portions of the project, I went with K3s - a lightweight solution for Kubernetes (link below). 
While I use Docker to build containers, I'm honestly more comfortable handling them with kubernetes at this point, so this decision was partially made based on comfortability level. 
The other side is that it's a lot easier to handle the kafka containers if they're all orchestrated as K8 pods vs. manually managed Docker containers. 
- K3s link: https://k3s.io/
  - Honestly seems like a pretty cool solution for anyone in the IoT space. Managing pods feels the exact same with kubectl in this as it does with a full K8s deployment.

Both yaml files were derived from the example values files for each technology. 
As a callout, I used Bitnami's helm charts and images for each. I've found that they generally do a good job for open source projects, although sometimes the documentation can be outdated/lacking.
Who am I to complain though, I'm just some internet schmuck riding the coattails of people who developed this for free lol. 

The default values are available at the below URLs:
- MongoDB: https://github.com/bitnami/charts/blob/main/bitnami/mongodb-sharded/values.yaml
- Kafka: https://github.com/bitnami/charts/tree/main/bitnami/kafka

___

### MongoDB Deployment:
#### Key differences between deployment and default values.yaml:
- Standalone deployment:
  - I don't particularly mind if the database crashes and then reboots because this is a non-production learning focused project. Also, I'm cheap and don't want to give AWS more money than I have to. 
- Authentication:
  - I set this section to false and passed in my kubernetes secret for the database admin credentials
- Set the service to NodePort
  - I'm using the standalone architecture, so I only need a single NodePort IP for external traffic out of the database/EC2 server.
  - I kept the MongoDB internal port as 27017 (the default)
  - I explicitly set the nodePort value to 31234, which allows external services (like the Kafka MongoDB connector) to reach MongoDB through the EC2 node's public or private IP on this port.

___

### Kafka Deployment:
#### Key differences between deployment and default values.yaml:
 - **Enabling of KRaft mode:**
   - It seems like Kafka is generally intending on deprecating ZooKeeper as the assisting container software for its brokers. I changed this setting to 'true' because I figured I might as well go with the flow when learning.
   - There's plenty of documentation online between the two, but a general summary is that KRaft keeps everything in-house within the kafka cluster vs. requiring an external cluster managed by ZooKeeper. Basically just makes things easier to manage going forwards.
 - **Reduced replica counts:**
   - I set both my controller and broker replicaCount fields to 1.
   - Reason being... I'm not made of money and no one's going to be using this data to make trades (Don't worry I'll be putting a big 'ol disclaimer on the front end page about this), so it doesn't really matter if something crashes and data is lost before the pods reboot.
   - Typically though, there should be multiple replicas of both the controllers and the brokers for a kafka cluster as a way to ensure high availability of the cluster. The other reason being that it improves throughput of messages for high event use cases.
 - **Resource limits for broker/controller pods and persistent storage defined:**
   - This is generically a good practice, but I defined resources for each with the below amounts because I know I'm operating this off of a single EC2 instance:
     - Controller: Allocated 250m CPU and 256Mi memory for both requests and limits.
       - Storage: 2gi
     - Broker: Allocated 500m CPU and 512Mi memory for both requests and limits.
       - Storage: 2gi
 - **Listener configuration:**
   - I configured a single PLAINTEXT listener on port 9092.
   - I'm running this very simply currently and have firewalls on my EC2s shut down for any external traffic coming from outside the server except for my local IP. 
   - This is something I'll have to fix at a later point - but the intent is to move this to a TLS configuration once I'm ready to have my visualizations be public facing.
 - **Adding the extraDeployment section for the MongoDB connector plugin:**
   - This portion took a lot of time for configuration as the documentation on it is missing some things. There is a default version of this on bitnami's github for kafka in the link above however. 
   - **About:**
     - I ran this in a distributed architecture. There's an option to run the connector in standalone, but I wanted to try for a more "production model" in my learning.
     - In standalone mode, a single Kafka Connect process acts as both a producer and consumer, running all connectors locally. That means if you're using it to ingest from a source and push to a sink, the same pod is handling both directions of data flow—reading from Kafka and writing to an external system (or vice versa). 
     - This setup works fine for lightweight use cases, but it's more prone to crashes under heavy load. Since everything runs in a single process, any failure brings the whole connector down, and there’s no automatic failover. 
     - By contrast, in distributed mode, the connector pod runs as part of a cluster of Kafka Connect workers. Each worker can handle specific tasks—like acting solely as a source or a sink—and Kafka itself manages the coordination, offsets, and rebalancing across workers. This not only improves fault tolerance, but also allows for scaling horizontally by adding more worker pods to share the load.
     - I configured this via the configmap section in the extraDeloyment portion of the yaml, but there's much more documentation available online if you want specifics.
   - **Things you need to do to get this to work:**
     - Make a kubernetes secret that has sensitive information about your MongoDB database:
       - Things like username/password/the IP it's on, etc.
       - Configure the connector's uri using this information.
       - Mount that secret to the main container section as an env variables so you can pull dynamically.
     - Make sure the port is pointing to the port you're using for the load balancer or NodePort used for external access in your MongoDB deployment.
       - Kafka writes its own groupid on deployment, but I was having a lot of trouble with 403 errors when I let it do that. I defined my own in this section.
     -Make sure the initContainer section downloads the connector pluging to the right folder location. 
         - You need to create that folder location and then mount it as a volume to be pulled from for association with the rest of the connector configuration.
         - Something Bitnami doesn't tell you on their documentation: you also need to make sure that the plugin location is actually able to be read as well.
           - I did this by applying the chmod command in the initContainer.
     - Create a config, offset, status, and an additional __consumer_offsets  topics within kafka prior to deploying the connector
       - Before deploying the connector, I had to manually create several internal Kafka topics: 
         - __consumer_offsets
         - __connect-configs
         - __connect-offsets
         - __connect-status
       - This part took a lot of trial and error. The issue, in hindsight was that I hadn’t deployed any producer yet. Kafka normally creates the __consumer_offsets topic automatically once a producer sends data and a consumer starts consuming. But if you're just spinning up a connector without any traffic yet, this auto-creation never kicks in. 
       - If you _don't_ do this and try and register the connector plugin via a POST to the Kafka Connect REST API, the only thing your receive is a vague timeout error amounting to that spaceballs gif of the two guys combing through the desert sand.
       - To be clear: 
         - You need the __connect-configs, __connect-offsets, and __connect-status topics for Kafka Connect to operate in distributed mode—these track configs, task state, and progress. These topics can be auto-created, but only if your Kafka broker allows automatic topic creation. __consumer_offsets is especially sneaky—it usually only gets created after producer/consumer activity begins, so in setups where Kafka Connect is the first service touching Kafka, you may need to manually create it beforehand. 
         - Wanted to point this out though because it's not really obvious in the documentation that this occurs and I spent a lot of time troubleshooting with both chatgpt and going back in time to crawl stackoverflow forums (I know, crazy right?) to figure out this specific issue. 


