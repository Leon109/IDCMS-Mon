#!/bin/bash

#删除文件中目录中的python文件＃号开头的注释文件

function del_comment_file()
{
    echo  'change file' $file
    sed -i '2,${/^\s*#/d}' $file
    
} 

function del_comment()
{
    for file in `ls `; do
        case $file in
        *.py)
        del_comment_file
        ;;
        *)
        if [ -d $file ]; then
            cd $file
            del_comment
            cd ..
        fi
        ;;
    esac
    done
}

DIR=$1

if [ ! -d $DIR ]; then
    echo "The not is directory"
    exit 1;
else
    cd $DIR
    del_comment    
fi
