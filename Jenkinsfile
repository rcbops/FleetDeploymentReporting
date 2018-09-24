def postActions(buildStatus, deleteEnv, mergeToMaster) {
    def status
    deleteEnv = deleteEnv.toBoolean()
    mergeToMaster = mergeToMaster.toBoolean()

    switch (buildStatus) {
        case 'SUCCESS':
            if (deleteEnv) {
              sh 'vagrant destroy -f'
            }
            if (mergeToMaster) {
              sh 'git checkout -b working_dev_branch'
              sh 'git checkout master'
              sh 'git merge working_dev_branch'
              sh 'git push origin master'
              status = 'is now green'
            }
            break

        case 'UNSTABLE':
            status = 'is now unstable..'
            break

        case 'FAILURE':
            status = 'has turned RED :('
            break
    }
    cleanWs()
}

pipeline {

  agent { label 'master' }

  parameters { 
    booleanParam(name: 'RUN_TEST', defaultValue: true, description: '')
    booleanParam(name: 'RUN_REMOTE', defaultValue: false, description: '')
    booleanParam(name: 'DELETE_ENV', defaultValue: true, description: '')
    booleanParam(name: 'MERGE_TO_MASTER', defaultValue: false, description: '')

    string(name: 'HOST_NAME', defaultValue: 'jenkins_snitch_test', description: '') 
  }

  stages {
    stage('Get Ansible Config from Git') {
      steps {
        withCredentials([usernameColonPassword(credentialsId: 'dan_git_creds', variable: 'GITHUB_AUTH')]) {       
          sh "git clone https://${GITHUB_AUTH}@github.com/dani4571/cloud_snitch_vagrant.git --branch jenkins_test"
        }
      }
    }
    stage('Build') {
      steps{
        withCredentials([string(credentialsId: 'RAX_USERNAME', variable: 'RAX_USERNAME'),
                         string(credentialsId: 'RAX_API_KEY', variable: 'RAX_API_KEY'),
                         string(credentialsId: 'RAX_REG', variable: 'RAX_REG'),
                         string(credentialsId: 'RAX_USERNAME', variable: 'RS_USERNAME'),
                         string(credentialsId: 'RAX_API_KEY', variable: 'RS_API_KEY'),]) {
          sh 'git branch; git show'
          sh 'export RS_REGION_NAME=DFW; rack files object download --container cloud-snitch-test-data --name james-newton-aio > neo4j_dump'
          sh 'vagrant up --provider=rackspace'
        }
      }
    }
  }

  post { 
    always { 
      withCredentials([string(credentialsId: 'RAX_USERNAME', variable: 'RAX_USERNAME'),
                         string(credentialsId: 'RAX_API_KEY', variable: 'RAX_API_KEY'),
                         string(credentialsId: 'RAX_REG', variable: 'RAX_REG')]) {

        postActions(currentBuild.currentResult, env.DELETE_ENV, env.MERGE_TO_MASTER)
      }
    }
  }
}
