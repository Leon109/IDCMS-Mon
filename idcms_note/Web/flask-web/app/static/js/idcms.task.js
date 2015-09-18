$(function(){
    // 导航切换，批量处理
    $('ul.sub-menu li').click(function(){
        $(this).addClass('active').siblings('li').removeClass('active')
        var id = $(this).attr('id')
        //变量组合使用＋号
        $('div#'+id).removeClass('hidden')
        $('div.content').not('#'+id).addClass('hidden')
    });
});

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
    //选择框是密码的时候输入栏类型变为passsword,选择其他的清空value值
    $('#subitem').change(function(){
        var change_item = $('#subitem').val()
        if(change_item=="password"){
            $('#subvalue').attr('type','password');
            $('#subvalue').val('');
        }else{
            $('#subvalue').attr('type','text');
            $('#subvalue').val('');
        }
    });
    // 批量选择选择框变更更改value 
    $('#batch-subitem').change(function(){
        $('#batch-subvalue').val('');
    });

    // 编辑删除
    // det 返回确认
    var det
    // 定位删除项目
    $('div.setting button#delete').click(function(){
        var id = $(this).attr('data-id');
        // 添加到提交项目的value中
        $('#subdelete').val(id);
    });
    // 定位修改项目
    $('div.setting button#change').click(function(){
        var id = $(this).attr('data-id');
        // 添加到提交项目的value中
        $('#subchange').val(id);
    });
    // 确定删除项目
    $('#confirm_delete').on('submit',function(e){
        e.preventDefault();
        var url = $(this).attr('action')
        var del_id = $('#subdelete').val()
        $.post(url, {id:del_id}, function(res){
            if (res=='OK'){
                det = true
                $('#tipModal').find('.modal-body').html('删除成功').end().modal('show')
            }else{
                $('#tipModal').find('.modal-body').html(res).end().modal('show')
            }
        });
    });
    // 确认修改项目
    $('#confirm_change').on('submit',function(e){
        e.preventDefault();
        var url = $(this).attr('action')
        var change_id = $('#subchange').val()
        var change_item = $('#subitem').val()
        var change_value = $('#subvalue').val()
        $.post(url, {id:change_id, item:change_item, value:change_value}, function(res){
            if (res=='OK'){
                det = true
                $('#tipModal').find('.modal-body').html('修改成功').end().modal('show')
            }else{
                $('#tipModal').find('.modal-body').html(res).end().modal('show')
            }   
        });  
    });
    
    //选择编辑删除
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
        var list_id = checkbox_list();
        if(list_id.length > 0){
            $('div.bs-modal-sm-batch-delete').modal('show')
        }else{
            $('#tipModal').find('.modal-body').html("没有选定任何删除的项目").end().modal('show')
        } 
    });

    $('#confirm_batch_delete').on('submit',function(e){
        e.preventDefault();
        var list_id = checkbox_list();
        var url = $(this).attr('action');
        var json_id = JSON.stringify(list_id)
        $.post(url, {list_id:json_id}, function(res){
            if (res=='OK'){
                //alert('删除成功')
                det = true
                $('#tipModal').find('.modal-body').html('批量删除成功').end().modal('show')
            }else{
                $('#tipModal').find('.modal-body').html(res).end().modal('show')
            }
        });
    });

    //批量修改
    $('#batch_change').click(function(){
        var list_id = checkbox_list();
        if(list_id.length > 0){ 
            $('div.bs-modal-sm-batch-setting').modal('show')
        }else{
            $('#tipModal').find('.modal-body').html("没有选定任何修改的项目").end().modal('show')
        }   
    }); 

    $('#confirm_batch_change').on('submit',function(e){
        e.preventDefault();
        var list_id = checkbox_list();
        var url = $(this).attr('action')
        var json_id = JSON.stringify(list_id)
        var change_item = $('#batch-subitem').val()
        var change_value = $('#batch-subvalue').val()
        $.post(url, {list_id:json_id, item:change_item, value:change_value}, function(res){
            if (res=='OK'){
                det = true
                $('#tipModal').find('.modal-body').html('批量修改成功').end().modal('show')
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

});


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
        }
    ];
    // 如果不是/cmdb/record字段最后连个搜索字段禁止排序
    var ban_sort = {"targets": [-1,-2], "orderable": false};
    var url_end = window.location.pathname;
    if(url_end != "/cmdb/record"){
        table_dict["columnDefs"].push(ban_sort)
    };
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
    });
});
