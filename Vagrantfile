Vagrant.configure("2") do |config|
  config.ssh.private_key_path = "~/.ssh/id_rsa"
  config.vm.provider :rackspace do |rs, override|
    override.vm.synced_folder ".", "/vagrant", type: "rsync"
    rs.username         = ENV['RAX_USERNAME']
    rs.api_key          = ENV['RAX_API_KEY']
    rs.rackspace_region = ENV['RAX_REG']
    rs.flavor           = /2 GB General Purpose v1/
    rs.image            = /Ubuntu 16.04/
    rs.server_name      = "jenkins_snitch_test_" + ENV['BUILD_NUMBER']
    rs.public_key_path  = "~/.ssh/id_rsa.pub"
  end


  config.vm.provision "shell", inline: <<-SHELL
     echo "Install Packages"
     sudo apt-get update
     sudo apt-get install -y python-pip python3.5
     sudo pip install virtualenv

     echo "Update Keys"
     ssh-keygen -q -N "" -f /root/.ssh/id_rsa
     cat /root/.ssh/id_rsa.pub >> /root/.ssh/authorized_keys

     echo "Link Ansible"
     ln -s /vagrant/cloud_snitch_vagrant/ansible /etc/ansible
     sudo cp /vagrant/neo4j_dump /opt

     echo "Create and Source Virtualenv"
     virtualenv --python=python3.5 /opt/venvs/cloudsnitch
     source /opt/venvs/cloudsnitch/bin/activate
     pip install ansible

     echo "Performing local installation"
     cd /vagrant/installation/local
     if [ #{ENV['RUN_TEST']} == true ]; then
       ansible-playbook testenv_install.yml
       cd /opt/web/cloud_snitch/web
       python manage.py test
     elif [ #{ENV['RUN_REAL']} == true ]; then
       ansible-playbook web_install.yml
       ansible-playbook neo4j_install.yml
       ansible-playbook sync_install.yml
       echo "Performing remote installation"
       cd /vagrant/installation/remote
       ansible-playbook collector_install.yml
       echo "Performing collection"
       sudo chown -R ubuntu:ubuntu /etc/cloud_snitch/data
       cd /vagrant/syndication
       ansible-playbook collect.yml
     fi

  SHELL
end
