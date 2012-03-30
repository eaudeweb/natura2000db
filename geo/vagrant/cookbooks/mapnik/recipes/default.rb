require_recipe "apt"

['python-mapnik'].each do |pkg|
  package pkg do
    :upgrade
  end
end
