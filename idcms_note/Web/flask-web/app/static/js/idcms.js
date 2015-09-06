// 导航切换，批量处理
$(function(){
    $('ul.sub-menu li').click(function(){
        $(this).addClass('active').siblings('li').removeClass('active')
        var id = $(this).attr('id')
        //变量组合使用＋号
        $('div#'+id).removeClass('hidden')
        $('div.content').not('#'+id).addClass('hidden')
    });
    $('input.batch').click(function(){
        if($("#batch_processing").is(":visible")){
            $("#batch_processing").hide();
        }else{
            $("#batch_processing").show();
        }
    });
})

// 删除修改函数
$(function(){
    //获取多选择框函数
    var checkbox_list = function(){
        var list = []
        $('input[name="checkList"]').each(function(){
            if($(this).prop("checked") === true){
                list.push(parseInt(($(this).attr('data-id'))));
            }
        });
        return list;
    };
    
    // 编辑删除
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
    //结果提示
    $('#tipModal button').click(function(){
        if(det){
            $("form.seek").submit()
        }
    });
    //权限编辑删除
    // 全选
    $("#checkAll").click(function(){
        if ($(this).prop("checked") === true) {
            $("input[name='checkList']").prop("checked", $(this).prop("checked"));
            $('#search span').addClass('checked');
            $('#search tbody tr').addClass('info');
        } else {
        $("input[name='checkList']").prop("checked", false);
            $('#search span').removeClass('checked');
            $('#search tbody tr').removeClass('info');
        }
    });
    // 多选
    $('#search tbody tr input[name="checkList"]').click(function(){
        var tr = $(this).parents('tr');
        tr.toggleClass('info');
        var $checkList = $('tr input[name="checkList"]');
        if ($checkList.length == $("tr input[name='checkList']:checked").length){
            $("#checkAll").prop("checked", true);
            $('thead span').addClass('checked');
        }else{
            $("#checkAll").prop("checked", false);
            $('thead span').removeClass('checked');
        }
    });
    
    //批量删除
    $('#batch_delete').click(function(){
        var x = checkbox_list();
        alert(x)
    });

})



$(document).ready(function() {

    //检查批量处理是否需要隐藏
    if($('input.batch').prop("checked") === true){
        $("#batch_processing").hide();
    };


    // DataTable
    var table_dict = {
        //分页
        paging: false,
        // 排序
        //ordering: false,
        //页面信息
        info: false,
        //分页
        //bLengthChange: false,
        //aLengthMenu:[50, 100],
        //表格太长，添加滚动
        dom: "<'row' <'col-md-12'T>><'row'<'col-md-6 col-sm-12'l><'col-md-6 col-sm-12'f>r><'table-scrollable't><'row'<'col-md-5 col-sm-12'i><'col-md-7     col-sm-12'p>>",
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
    };
    
    //处理隐藏和禁止排序
    var defs = [];
    $('input[name="hidden"]:checked').each(function(){    
            defs.push(parseInt(($(this).attr('data-column'))));
    });
    table_dict["columnDefs"] = [
        {
        "targets": defs,
        "visible": false
        },
        {
        "targets": [-1,-2],
        "orderable": false
        }
    ]
    // 运行
    var table = $('#search').DataTable( 
        table_dict
    );
    
    //点击隐藏
    $('input.toggle-vis').click(function (e) {
        //e.preventDefault();
 
        // Get the column API object
        var column = table.column( $(this).attr('data-column') );
 
        // Toggle the visibility
        column.visible( ! column.visible() );
    } );
} );
