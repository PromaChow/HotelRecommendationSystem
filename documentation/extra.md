
## Lambda Process

Created the `lambda_data_gathering.py` file with the logic of the data gathering, we have to then package it and add it to the terraform folder using the following commands: 

- First create a dependencies folder and type the following command:
    ```bash
    pip install -r requirements.txt -t lambda/data_gathering/
    cp src/lambda_data_gathering.py lambda/data_gathering/
    cp src/secrets_manager.py lambda/data_gathering/
    ```

- Then package the lambda functionality into a zip file
    ```bash
    cd lambda/data_gathering/
    zip -r ../../tf/lambda_data_gathering.zip ./*
    ```

We then re-applied the terraform commands to apply the changes into out AWS account. 

To test the lambda process, we can go the the AWS Console, click on Lmabda > data_gathering_lambda > Test and test a single query: 
```json
{
  "region": "Andorra la Vella",
  "num_hotels": 1,
  "num_reviews": 1
}
```