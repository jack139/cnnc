var tnm_dict = {
        'T' : '原发肿瘤',
        'N' : '区域淋巴结',
        'M' : '远处转移',
        'G' : '组织学分级/分化程度/肿瘤分级',
        'L' : '肿瘤位置',
        'S' : '血清学标记物',
        'Y' : '年龄',
        'PSA' : 'PSA值',
        'HE' : '肿瘤核分裂',
        'RISK' : '预后风险评估',
        'HER2' : 'HER2',
        'ER' : 'ER',
        'PR' : 'PR',
    };
var tnm_data={};
var stage_rec=[];
var user_select={
        'T' : '',
        'N' : '',
        'M' : '',
        'G' : '',
        'L' : '',
        'S' : '',
        'Y' : '',
        'PSA' : '',
        'HE' : '',
        'RISK' : '',
        'HER2' : '',
        'ER' : '',
        'PR' : '',
        'stage' : '', /* 分期结果 */
    };

function checkSelect(evt) {
    if (evt.target.value == "8") {
        $('#sub_cate_7').hide();
        $('#sub_cate_8').show();
    }
    else{
        $('#sub_cate_8').hide();
        $('#sub_cate_7').show();
    }
    return true;
}

function draw_tnm_node(page_id, tnm_name, data, data_memo){
    /*
    var text = '';
    $.each(data, function(index, value){
        var t = value['code'];
        text += t[0]+t[1]+t[2]+t[3]+t[4];
        text += (t[5].length==0)?'':'('+t[5]+')'; 
        text += ' : ' + value['desc'] + '\n';
    });
    */
    var node = new Node(data, tnm_name, 'tnm', page_id);
    node.appendToPaper();

    if (data_memo.length>0 && data_memo.trim()!="<br>"){ /*为空时可能只有<BR>*/
        node = new Node(data_memo, tnm_name, 'memo', page_id);
        node.appendToPaper();
    }
}


function check_tnm_status(){
    var first = true;

    $.each(Object.keys(tnm_dict), function(index, tnm_name){
        var node_tnm = '#nodediv_'+tnm_name+'_tnm';
        var node_memo = '#nodediv_'+tnm_name+'_memo';
        var node_title = '#nodediv_'+tnm_name+'_title';
        var node_bar = '#nodediv_'+tnm_name+'_bar';

        /* 无数据则忽略 */
        if (!tnm_data['tnm'].hasOwnProperty(tnm_name)){
            tnm_data['tnm'][tnm_name]=[];
            return true;
        }

        if (tnm_data['tnm'][tnm_name].length==0) return true;

        if ($(node_title).text().length>0){
            $(node_bar).show();
            $(node_tnm).hide();
            $(node_memo).hide();
        } else {
            if (first){
                $(node_bar).show();
                $(node_tnm).show();
                $(node_memo).show();
                first = false;
            } else {
                $(node_bar).hide();
                $(node_tnm).hide();
                $(node_memo).hide();                
            }
        }
    });

    if (first){
        /* 可以计算结果了 */
        var session_id = $("#session_id").val();
        var page_id = $("#page_id").val();

        $('#stage_result').text('');
        $('#nodediv_stage').hide();

        wx_interface(
            "tnm_stage",
            {
                session_id : session_id,
                page_id    : page_id,
                tnm        : JSON.stringify(user_select),
            },
            function(data){
                var text="";
                if (tnm_data.hasOwnProperty('ret_set')){
                    $.each(["T", "N", "M", "G", "L", "S", "Y", "PSA", "HE", "RISK", "HER2", "ER", "PR"], function(index, value){
                        if (tnm_data['ret_set'][value]==1)
                            text += user_select[value];
                    });
                    text += ' '+data['stage'];
                }
                else{
                    text = user_select['T']+user_select['N']+user_select['M']+' '+data["stage"];
                }
                user_select['stage'] = data["stage"]; 
                $('#stage_result').text(text);
                $('#stage_result_desc').html(text2HTML(data["desc"]));
                if (tnm_data['rich_text'].length>0){
                    $("#stage_rich_text").html(filterNote(tnm_data['rich_text']));
                }
                $('#nodediv_stage').show();
                TDAPP.onEvent("计算分期", "计算成功"); 
            }
        );
        
    }
}

/* 页面初始化 */
$(function(){
    var session_id = $("#session_id").val();
    var parent_id = $("#parent_id").val();
    var page_id = $("#page_id").val();

    var show_cate = function(session){
        /* 生成目录 */
        wx_interface(
            "tnm_cate",
            {
                session_id : session_id,
                cate_id : $("#cate_id").val(),
            },
            function(data){

                var tr_html;
                $.each(data['data'], function(index, i){
                    if (i['type']=='cancer'){
                        tr_html += "<tr><td>";
                        tr_html += i['gen'] + '<a href="/wx/tnm_init?session_id=' + session_id + '&page_id=' + i['_id'] 
                            + '&parent_id=' + i['_id'] + '">' 
                            + i['tnm_name'] + '</a>';
                        tr_html += "</td></tr>";
                    } else {
                        tr_html += "<tr><td>" + i['name'] + "</td></tr>";
                    }
                });

                $("#table_body").html(tr_html);

            }
        );
    };

    var show_page = function(session, page){
        var only_one = getUrlParam("only_one");

        wx_interface(
            "tnm_page",
            {
                session_id : session,
                page_id    : page,
                only_one   : only_one,
            },
            function(data){
                if (data['only_one']>1){  /* 子目录 */
                    var tr_html_7="", tr_html_8="";
                    $.each(data['data'], function(index, i){
                        var tr_html="";

                        tr_html += "<br/><div class='jump_color2'>";
                        tr_html += '<a href="/wx/tnm_init?session_id=' + session_id + '&page_id=' + i['_id'] 
                            + '&parent_id=' + i['_id'] + '&only_one=1">' 
                            + i['tnm_name'];
                        var coma = (i['tnm_subname1'].length>0 && i['tnm_subname2'].length>0)?'，':'';
                        tr_html += (i['tnm_subname1'].length==0 && i['tnm_subname2'].length==0)?"":"【" + i['tnm_subname1'] + coma + i['tnm_subname2'] + "】";
                        tr_html += "</a></div>";
                        tr_html += (i['use_at'].length==0)?"":"<div><i>适用于：" + i['use_at'] + "</i></div>";

                        if (i['version']=='8') tr_html_8 += tr_html;
                        else tr_html_7 += tr_html;
                    });

                    $("#sub_cate_7").html(tr_html_7);
                    $("#sub_cate_8").html(tr_html_8);

                    $("#tnm_name").text(data['data'][0]['tnm_name']);

                    if (tr_html_7.length>0 && tr_html_8.length>0){
                        $("#version_select").show();
                        $("#sub_cate_8").show()
                    } else if (tr_html_7.length>0){
                        $("#verison_number").text("7");
                        $("#version_tag").show();
                        $("#sub_cate_7").show()

                    } else if (tr_html_8.length>0){
                        $("#verison_number").text("8");
                        $("#version_tag").show();
                        $("#sub_cate_8").show()
                    }

                } else {  /* tnm 分期页面 */
                    tnm_data = data['data'];

                    $("#version").val(tnm_data['version']);
                    $("#verison_number").text(tnm_data['version']);
                    $("#version_tag").show();
                    $("#tnm_name").text(tnm_data['tnm_name']);
                    if (tnm_data['use_at'].length>0)
                        $("#use_at").text('适用于：'+tnm_data['use_at']);
                    
                    TDAPP.onEvent("打开页面", tnm_data['tnm_name']+' '+tnm_data['version']);

                    draw_tnm_node(page, 'T', tnm_data['tnm']['T'], tnm_data['t_memo']);
                    draw_tnm_node(page, 'N', tnm_data['tnm']['N'], tnm_data['n_memo']);
                    draw_tnm_node(page, 'M', tnm_data['tnm']['M'], tnm_data['m_memo']);
                    draw_tnm_node(page, 'G', tnm_data['tnm']['G'], tnm_data['g_memo']);
                    draw_tnm_node(page, 'L', tnm_data['tnm']['L'], '');
                    draw_tnm_node(page, 'S', tnm_data['tnm']['S'], '');
                    draw_tnm_node(page, 'Y', tnm_data['tnm']['Y'], '');
                    draw_tnm_node(page, 'PSA', tnm_data['tnm']['PSA'], '');
                    draw_tnm_node(page, 'HE', tnm_data['tnm']['HE'], '');
                    draw_tnm_node(page, 'RISK', tnm_data['tnm']['RISK'], '');
                    draw_tnm_node(page, 'HER2', tnm_data['tnm']['HER2'], '');
                    draw_tnm_node(page, 'ER', tnm_data['tnm']['ER'], '');
                    draw_tnm_node(page, 'PR', tnm_data['tnm']['PR'], '');

                    check_tnm_status();
                    
                    $("#use_at_paper").show();

                    $(".sidebar.top").trigger("sidebar:open", [{ speed: 300 }]);
                }
            }
        );
    };


    //$(".sidebar.left").sidebar().trigger("sidebar:open");
    $(".sidebar.left").sidebar({side: "left"});
    $(".sidebar.bottom").sidebar({side: "bottom"});
    $(".sidebar.top").sidebar({side: "top"});

    var startX, startY;
    $('.sidebar.bottom').on('touchstart',function(e){
        startX = e.originalEvent.changedTouches[0].pageX;
        startY = e.originalEvent.changedTouches[0].pageY;
        e.stopPropagation();
    });

    $('.sidebar.bottom').on('touchend',function(e){
        var moveEndX = e.originalEvent.changedTouches[0].pageX;
        var moveEndY = e.originalEvent.changedTouches[0].pageY;
        if (moveEndY==startY && moveEndX==startX){
            $(".sidebar.bottom").trigger("sidebar:close", [{ speed: 300 }]);
        }
        e.stopPropagation();
    });

    $('.sidebar.left').on('touchstart',function(e){
        startX = e.originalEvent.changedTouches[0].pageX;
        startY = e.originalEvent.changedTouches[0].pageY;
        e.stopPropagation();
    });

    $('.sidebar.left').on('touchend',function(e){
        var moveEndX = e.originalEvent.changedTouches[0].pageX;
        var moveEndY = e.originalEvent.changedTouches[0].pageY;
        if (moveEndY==startY && moveEndX==startX){
            $(".sidebar.left").trigger("sidebar:close", [{ speed: 300 }]);
        }
        e.stopPropagation();
    });

    $('#bar_close').on('click touchstart', function(e) {
        $(".sidebar.left").trigger("sidebar:close", [{ speed: 300 }]);
        e.stopPropagation();
    });
    $('#bar_open').on('click touchstart', function(e) {
        $(".sidebar.left").trigger("sidebar:open", [{ speed: 300 }]);
        e.stopPropagation();
    });

    /* 点框架关闭底栏 */
    $("#frame").on('click touchstart', function(e){
       $(".sidebar.bottom").trigger("sidebar:close", [{ speed: 300 }]); 
       $(".sidebar.left").trigger("sidebar:close", [{ speed: 300 }]);
       //e.stopPropagation();
       //e.preventDefault();
    })

    show_cate(session_id);
    show_page(session_id, page_id);

});


function getUrlParam(name) {
    var reg = new RegExp("(^|&)" + name + "=([^&]*)(&|$)"); //构造一个含有目标参数的正则表达式对象
    var r = window.location.search.substr(1).match(reg);  //匹配目标参数
    if (r != null) return unescape(r[2]); return null; //返回参数值
}