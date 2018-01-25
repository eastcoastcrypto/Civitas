#!/bin/sh

cd $1/Contents/Frameworks
dirs=($(find . -type d -maxdepth 1 \! -name . \! -name .. ))
for dir in "${dirs[@]}"; do
  name=${dir:2:${#dir}-12}
  echo name=$name

  echo pushd $dir
  pushd $dir

  echo pwd=`pwd`
  
  echo mv Resources Versions/5/
  mv Resources Versions/5/

  echo ln -s Versions/Current/$name $name
  ln -s Versions/Current/$name $name
  echo ln -s Versions/Current/Resources Resources
  ln -s Versions/Current/Resources Resources

  echo popd
  popd
done