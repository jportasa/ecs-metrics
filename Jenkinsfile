#!groovy

@Library('jenkins-shared-library') _

lambdaPipeline {
    lambdaGenericFunctionName = 'ecs-metrics'
    slackNotificationChannel = '#devops-events'
    projectName = 'ecs-metrics'
    s3BucketFolder = 'ecs-metrics'
    s3ZipFile = 'function.zip'
}
