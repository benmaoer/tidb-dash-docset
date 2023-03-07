#!/usr/bin/env bash

while true
do
    case $1 in
      -v|--version) 
        version=$2
        shift
        ;;
      -c|--clear) 
        clear=$2
        shift
        ;;        
      -h|--help)
        usage
        shift
        exit 0
        ;;
      *)
        usage
        shift
        break
        ;;
    esac
    shift
done

usage()
{
    echo "Usage: $0 [ -v | --version ] [ -c | --clear ] [ -h | --help ] "
}


if [ -z "${version}" ]; then
    version="6.5"
fi
basedir=/tmp/tidb

if [ -z ${clear} ]; then
    rm -rf ${basedir}/target
fi


mkdir -p ${basedir}
git clone git@github.com:benmaoer/tidb-dash-docset.git ${basedir}/tidb-dash-docset
pandoc_cmdline="pandoc --embed-resources --standalone --template=GitHub.html5 --toc -t html5 --default-image-extension=jpg+png --resource-path=${basedir}/origin/media --filter=${basedir}/tidb-dash-docset/url.py --lua-filter=${basedir}/tidb-dash-docset/fixpath.lua "


mkdir -p ${basedir}/origin ${basedir}/target
git clone git@github.com:pingcap/docs-cn.git ${basedir}/origin 
cd ${basedir}/origin 
git checkout -b release-${version} 
for dirname in $(find . -type d |grep -vE ".git|.github|media|release|dashboard|resource\/" | tail -n +2)
do
	mkdir -p ${basedir}/target/${dirname}
    cd  ${basedir}/origin/${dirname}
    for file in $(find . -iname "*.md" -type f -maxdepth 1)
    do
        newfile=${basedir}/target/${dirname}/${file%%md*}html
        $pandoc_cmdline -M webroot=.. -o ${newfile} ${file}
        sed -i '' -e '/^\<video*/d' ${newfile}
    done
done


cd  ${basedir}/origin
for file in $(find . -iname "*.md" -type f -maxdepth 1)
do
    $pandoc_cmdline -M webroot=. -o ${basedir}/target/${file%%md*}html ${file}
    sed -i '' -e '/^\<video*/d' ${basedir}/target/${file%%md*}html
done

cd ${basedir}/target && dashing init TiDB && dashing build TiDB
for file in $(find ${basedir}/target/tidb.docset -iname "*.html" -type f)
do
    sed -i '' 's|content:"&nbsp;"|content:" "|g' ${file}
done

python3 ${basedir}/tidb-dash-docset/generate_index.py
cd ${basedir}/target && tar --exclude='.DS_Store' -cvzf TiDB.tgz TiDB.docset


