// 导航切换
$(function(){
    $('div.side li').click(function(){
        $(this).addClass('active').siblings('li').removeClass('active')
        var id = $(this).attr('id')
        //变量组合使用＋号
        $('div#'+id).removeClass('hide')
        $('div.content').not('#'+id).addClass('hide')
    });
})

// 删除修改函数
$(function(){
    var det
    // 定位删除项目
    $('div.setting button#delete').click(function(){
        var id = $(this).attr('data-id')
        $('#subdelete').val(id);
    });
    // 定位修改项目
    $('div.setting button#change').click(function(){
        var id = $(this).attr('data-id')
        $('#subchange').val(id);
    });
    // 确定删除项目
    $('#confirmdeldelete').on('submit',function(e){
        e.preventDefault();
        var url = $(this).attr('action')
        var change_data = $('#subdelete').val()
        $.post(url, {id:change_data}, function(res){
            if (res=='OK'){
                //alert('删除成功')
                det = true
                $('#tipModal').find('.modal-body').html('删除成功').end().modal('show')
            }else{
                $('#tipModal').find('.modal-body').html(res).end().modal('show')
            }
        });
    });
    // 确认修改项目
    $('#confirmdelchange').on('submit',function(e){
        e.preventDefault();
        var url = $(this).attr('action')
        var change_id = $('#subchange').val()
        var change_item = $('#subitem').val()
        var change_value = $('#subvalue').val()
        var sub = {id:change_id, item:change_item, value:change_value}
        $.post(url, {id:change_id, item:change_item, value:change_value}, function(res){
            if (res=='OK'){
                det = true
                $('#tipModal').find('.modal-body').html('修改成功').end().modal('show')
            }else{
                $('#tipModal').find('.modal-body').html(res).end().modal('show')
            }   
        });  
    });
    // 结果提示
    $('#tipModal button').click(function(){
        if(det){
            location.reload(true)
        }
    });
})


// DataTable
$(document).ready(function() {
    var table = $('#search').DataTable( {
        aLengthMenu:[50, 100],//每页显示数量
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
