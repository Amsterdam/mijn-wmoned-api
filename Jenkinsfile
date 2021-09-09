#!groovy

def tryStep(String message, Closure block, Closure tearDown = null) {
    try {
        block()
    }
    catch (Throwable t) {
        slackSend message: "${env.JOB_NAME}: ${message} failure ${env.BUILD_URL}", channel: '#ci-channel', color: 'danger'

        throw t
    }
    finally {
        if (tearDown) {
            tearDown()
        }
    }
}

def retagAndPush(String imageName, String currentTag, String newTag)
{
    def regex = ~"^https?://"
    def dockerReg = "${DOCKER_REGISTRY_HOST}" - regex
    sh "docker tag ${dockerReg}/${imageName}:${currentTag} ${dockerReg}/${imageName}:${newTag}"
    sh "docker push ${dockerReg}/${imageName}:${newTag}"
}

node {
    stage("Checkout") {
        checkout scm
    }

    stage('Test') {
        tryStep "test", {
            sh "docker-compose -p focus -f app/jenkins/test/docker-compose.yml build && " +
               "docker-compose -p focus -f app/jenkins/test/docker-compose.yml run -u root --rm test"
        }, {
            sh "docker-compose -p focus -f app/jenkins/test/docker-compose.yml down"
        }
    }

    stage("Build image") {
        tryStep "build", {
            docker.withRegistry("${DOCKER_REGISTRY_HOST}",'docker_registry_auth') {
                def image = docker.build("mijnams/wmoned:${env.BUILD_NUMBER}", "app")
                image.push()
            }
        }
    }
}

String BRANCH = "${env.BRANCH_NAME}"

if (BRANCH == "master" || BRANCH == "test-acc") {

    node {
        stage('Push acceptance image') {
            tryStep "image tagging", {
                docker.withRegistry("${DOCKER_REGISTRY_HOST}",'docker_registry_auth') {
                    docker.image("mijnams/wmoned:${env.BUILD_NUMBER}").pull()
                    // The Image.push() function ignores the docker registry prefix of the image name,
                    // which means that we cannot re-tag an image that was built in a different stage (on a different node).
                    // Resort to manual tagging to allow build and tag steps to run on different Jenkins slaves.
                    retagAndPush("mijnams/wmoned", "${env.BUILD_NUMBER}", "acceptance")
                }
            }
        }
    }

    node {
        stage("Deploy to ACC") {
            tryStep "deployment", {
                build job: 'Subtask_Openstack_Playbook',
                    parameters: [
                        [$class: 'StringParameterValue', name: 'INVENTORY', value: 'acceptance'],
                        [$class: 'StringParameterValue', name: 'PLAYBOOK', value: 'deploy.yml'],
                        [$class: 'StringParameterValue', name: 'PLAYBOOKPARAMS', value: "-e cmdb_id=app_mijn-wmoned"]
                    ]
            }
        }
    }
}

if (BRANCH == "master") {
    stage('Waiting for approval') {
        slackSend channel: '#ci-channel', color: 'warning', message: 'mijn-wmoned-api is waiting for Production Release - please confirm'
        input "Deploy to Production?"
    }

    node {
        stage('Push production image') {
            tryStep "image tagging", {
                docker.withRegistry("${DOCKER_REGISTRY_HOST}",'docker_registry_auth') {
                    docker.image("mijnams/wmoned:${env.BUILD_NUMBER}").pull()
                    retagAndPush("mijnams/wmoned", "${env.BUILD_NUMBER}", "production")
                    retagAndPush("mijnams/wmoned", "${env.BUILD_NUMBER}", "latest")
                }
            }
        }
    }

    node {
        stage("Deploy") {
            tryStep "deployment", {
                build job: 'Subtask_Openstack_Playbook',
                    parameters: [
                        [$class: 'StringParameterValue', name: 'INVENTORY', value: 'production'],
                        [$class: 'StringParameterValue', name: 'PLAYBOOK', value: 'deploy.yml'],
                        [$class: 'StringParameterValue', name: 'PLAYBOOKPARAMS', value: "-e cmdb_id=app_mijn-wmoned"]
                    ]
            }
        }
    }
}
