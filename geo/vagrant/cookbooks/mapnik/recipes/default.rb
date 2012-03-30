require_recipe "apt"


apt_repository "mapnik-nightly-2.0" do
  uri "http://ppa.launchpad.net/mapnik/nightly-2.0/ubuntu"
  distribution "lucid"
  components ["main"]
  keyserver "keyserver.ubuntu.com"
  key "5D50B6BA"
end


['python-mapnik', 'python-virtualenv', 'python-imaging'].each do |pkg|
  package pkg do
    :upgrade
  end
end
