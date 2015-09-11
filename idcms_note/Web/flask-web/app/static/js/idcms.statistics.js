//统计分析功能
function echarts_run(url){
    var res = null;
    $.ajax({
      url: url,
      async: false,
      dataType: 'json',
      success: function (json){
        res = json;
      }
    });

    require.config({
        paths: {
            echarts: '/static/echarts/build/dist'
        }
    });
    
    require(
        [
            'echarts',
            'echarts/theme/macarons',
             res.graph
        ],

        function (ec, theme) {
            var myChart = ec.init(document.getElementById('main'), theme); 
            var option = res.option;
            myChart.setOption(option);
        }
    );
};

$(document).ready(function(){
    var url = null;
    $('ul.sub-menu li').click(function(){
        $(this).addClass('active').siblings('li').removeClass('active')
        base_url = $(this).attr('url')
        url = base_url
        var id = $(this).attr('id')
        $('div#'+id).removeClass('hidden')
        $('div.content').not('#'+id).addClass('hidden')
        if (id=='site'){
            url = base_url + $('#site_info').val()
        }
        $('#site_info').change(function(){
            url = base_url + $(this).val()
            echarts_run(url)
        });
        echarts_run(url)
    });
    url = "/cmdb/statistics/base_info"
    echarts_run(url)
});
