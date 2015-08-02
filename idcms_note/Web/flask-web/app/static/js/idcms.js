$(function(){
    // 导航切换
    $('div.side li').click(function(){
        $(this).addClass('active').siblings('li').removeClass('active')
        var id = $(this).attr('id')
        //alert(id)
        //变量使用＋号
        $('div#'+id).removeClass('hide')
        $('div.content').not('#'+id).addClass('hide')
    })
})

$(function(){
    // 定位删除项目
    $('div.change button#delete').click(function(){
        var id = $(this).attr('data-id')
        $('#subdelete').val(id);
    });
    // 定位修改项目
    $('div.change button#setting').click(function(){
        var id = $(this).attr('data-id')
        alert(id)
    });
    // 确定删除项目
    $('#confirmdel').on('submit',function(e){
        e.preventDefault();
        var url = $(this).attr('action')
        var del_data = $('#subdelete').val()
        $.post(url, {id:del_data}, function(res){
            if (res=='ok') {
                //alert('删除成功')
                $('#tipModal').find('.modal-body').html('删除成功').end().modal('show')
            }else{
                $('#tipModal').find('.modal-body').html(res).end().modal('show')
            }
        });
    // 结果提示
    $('#tipModal button').click(function(){
        location.reload(true)
       });
    });
})


// DataTable
$(document).ready(function() {
    var table = $('#search').DataTable( {
        language: {
            "sLengthMenu": "显示 _MENU_ 项结果",
            "sZeroRecords": "没有匹配结果",
            "sEmptyTable": "表中数据为空",
            "sInfoEmpty": "显示第 0 至 0 项结果，共 0 项",
            "sInfo": "显示第 _START_ 至 _END_ 项结果，共 _TOTAL_ 项",
            "sSearch": "搜索:",
            "oPaginate": {
                "sFirst": "首页",
                "sPrevious": "上页",
                "sNext": "下页",
                "sLast": "末页"
            }
        },
    } );

    $('a.toggle-vis').on( 'click', function (e) {
        e.preventDefault();
 
        // Get the column API object
        var column = table.column( $(this).attr('data-column') );
 
        // Toggle the visibility
        column.visible( ! column.visible() );
    } );
} );
