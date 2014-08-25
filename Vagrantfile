# -*- mode: ruby -*-
# vi: set ft=ruby :

VAGRANTFILE_API_VERSION = "2"

Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|
  config.vm.box = "precise64"
  config.vm.box_url = "http://files.vagrantup.com/precise64.box"

  config.vm.network "private_network", ip: "192.168.100.100"
  config.vm.network :forwarded_port, guest: 8000, host: 8000
  config.vm.network :forwarded_port, guest: 8983, host: 8983

  config.vm.provision :shell, :inline => "apt-get update"

  config.vm.provision :shell, :inline => "apt-get install -y postgresql postgresql-contrib python-dev python-pip libpq-dev git-core build-essential"

  config.vm.provision :shell, :inline => "sudo apt-get -y install curl python-software-properties unzip"
  config.vm.provision :shell, :inline => "sudo add-apt-repository -y ppa:webupd8team/java"
  config.vm.provision :shell, :inline => "sudo apt-get update"
  config.vm.provision :shell, :inline => "echo oracle-java7-installer shared/accepted-oracle-license-v1-1 select true | sudo /usr/bin/debconf-set-selections"
  config.vm.provision :shell, :inline => "sudo apt-get -y install oracle-java7-set-default"
  config.vm.provision :shell, :inline => "export JAVA_HOME='/usr/lib/jvm/java-7-oracle/jre'"

  # download and unzip solr 3.5.0, if not yet existing
  config.vm.provision :shell do |shell|
    shell.inline = <<-EOS
      set -e
      if [ ! -d apache-solr-3.5.0/ ]
      then
        curl -O https://archive.apache.org/dist/lucene/solr/3.5.0/apache-solr-3.5.0.tgz
        tar xvzf apache-solr-3.5.0.tgz
      else
        echo "Solr already deployed."
      fi
    EOS
  end




  # Generate config files and initialize DB
  config.vm.provision :shell do |shell|
    shell.inline = <<-EOS
      set -e

      sudo -u postgres psql -c "DROP DATABASE IF EXISTS kikar"
      sudo -u postgres psql -c "DROP ROLE IF EXISTS kikar"
      sudo -u postgres psql -c "CREATE USER kikar WITH PASSWORD 'kikar'"
      sudo -u postgres psql -c "CREATE DATABASE kikar TEMPLATE=template0 ENCODING='UTF8' LC_CTYPE='en_US.utf8' LC_COLLATE='en_US.UTF-8'"
    EOS
  end

  # pip requirements
  config.vm.provision :shell do |shell|
    shell.inline = <<-EOS
      set -e
      pwd -P
      # Do 2 pip tries as sometimes repositories fail to respond
      PIP="pip install -r /vagrant/requirements/vps.txt"
      $PIP || $PIP
    EOS
  end

  # Django setup
  config.vm.provision :shell do |shell|
    shell.inline = <<-EOS
      set -e
      pwd -P
      cd /vagrant/kikar_hamedina/
      pwd -P
      python manage.py syncdb --noinput
      [ -f ../devOps/user_backup.json ] && python manage.py loaddata ../devOps/user_backup.json
      python manage.py dumpdata --indent=4 auth > ../devOps/user_backup.json
      for m in core persons mks links facebook_feeds video; do
        python manage.py migrate $m
      done
      for f in 1001_1001 1001_1002 1001_1003 1001_1004; do
        gunzip facebook_feeds/fixtures/${f}.json.gz
      done
      for f in data_fixture_planet data_fixture_mks data_fixture_facebook_feeds 1001_1001 1001_1002 1001_1003 1001_1004 1002_1005 1002_1006 1003_1007; do
        python manage.py loaddata ${f}.json
      done
      for f in 1001_1001 1001_1002 1001_1003 1001_1004; do
        gzip facebook_feeds/fixtures/${f}.json
      done
      python manage.py build_solr_schema --using=solr_schema_template.xml > schema.xml
      mv schema.xml ../apache-solr-3.5.0/example/solr/conf/schema.xml
      cd ../apache-solr-3.5.0/example/
      export mysecret=kikar
      java -DSTOP.PORT=8079 -DSTOP.KEY=$mysecret -jar start.jar &
      cd ../../kikar_hamedina/
      python manage.py fetchfeedproperties || true
      python manage.py fetchfeedstatuses
      python manage.py rebuild_index --noinput
    EOS
  end

  config.vm.provision :shell do |shell|
    shell.inline = <<-EOS
      echo 'exec python /vagrant/kikar_hamedina/manage.py runserver 0.0.0.0:8000' > /etc/init/kikar.conf
      start kikar
    EOS
  end
end
