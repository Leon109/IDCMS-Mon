$(function(){
    $('div.side li').click(function(){
        $(this).addClass('active').siblings('li').removeClass('active')
        var id = $(this).attr('id')
        //alert(id)
        //变量使用＋号
        $('div#'+id).removeClass('hide')
        $('div.content').not('#'+id).addClass('hide')
    })
})
