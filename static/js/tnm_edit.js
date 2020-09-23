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
var tnm_rec={
        'T' : [],
        'N' : [],
        'M' : [],
        'G' : [],
        'L' : [],
        'S' : [],
        'Y' : [],
        'PSA' : [],
        'HE' : [],
        'RISK' : [],
        'HER2' : [],
        'ER' : [],
        'PR' : [],
    };
var stage_rec=[];

function init_something(){
    $('#save_button').click(function(){
        tnm_save();
    });

    $('#stage_add').click(function(){
        stage_edit(stage_rec.length, true);
    });        

    /* 初始化按钮 */
    /*
    $('#T_add').click(function(){
        tnm_edit("原发肿瘤", 'T', tnm_rec['T'].length, true);
    });
    */
    $.each(Object.keys(tnm_dict), function(index, value){
        $('#'+value+'_add').click(function(){
            tnm_edit(tnm_dict[value], value, tnm_rec[value].length, true);
        });        
    });

    /* 初始化数据 */
    $.each(Object.keys(tnm_dict), function(index, value){
        $.each(tnm_rec[value], function(i, v){
            var div_html = tnm_html(tnm_dict[value], value, i, v['code'][0], v['code'][1], v['code'][2], 
                v['code'][3], v['code'][4], v['code'][5], v['desc'], v['weight'], v['grey']);
            $('#'+value+'_list').append(div_html); 
        });
    });

    /* stage_html(stage_num, stage){ */
    $.each(stage_rec, function(i, v){
        var div_html = stage_html(i, v);
        $('#stage_list').append(div_html); 
    });
};


function highlight_text(text){
    /* 高亮 花括号 */
    text = text.replace(/\{.*?\}/g, function($0){ 
        var page_code=$0.substr(1,$0.length-2);
        return "<span style='background-color:#aee;color:#d00;'>"+page_code+"</span>";
    });

    /* 注释 方括号 */
    text = text.replace(/\[[\s\w-*#§¶†‡•Ü|]+\]/g, function($0){ 
        var note_code=$0.substr(1,$0.length-2);
        var p = note_code.lastIndexOf('-');
        return " <sup style='color:#ff1493;'>["+note_code.substr(p+1).replace('#','%23')+"]</sup> ";
    });

    /* 跳转 @() */
    text = text.replace(/\@\(.*?\)/g, function($0){ 
        var page_code=$0.substr(2,$0.length-3);
        return " <span style='color:#00d;'>(<u>"+page_code+"</u>)</span> ";
    });

    return text;
}

function tnm_remove(tnm_1, tnm_num){
    alertify.confirm("请确认 ...", "确定要删除吗？",
        function(){
            $("#"+tnm_1+'_'+tnm_num).remove();
            tnm_rec[tnm_1][tnm_num]=null;
            history.go(-1);
        },
        function(){
            history.go(-1);
    });
}

/* 参数： 标题， 主编码， tnm数据, 页面项目序号 */
function tnm_edit(title, tnm_1, tnm_num, is_new){
    var tnm;

    if (is_new){
        tnm = {
            'code' : ['', tnm_1, '', '', '', ''],
            'desc' : '',
            'weight' : 999,
        }
    }
    else
        tnm = tnm_rec[tnm_1][tnm_num];

    var dlgContentHTML = '<div id="dlgContentHTML">' + 
        '<p> 编码 </p>' +
        '<span>' +
        '    <select name="t_0" id="t_0">' +
        '        <option value="" '+ ((tnm['code'][0]=="")?"selected":"") +'>(空)</option>' +
        '        <option value="p" '+ ((tnm['code'][0]=="p")?"selected":"") +'>p</option>' +
        '        <option value="c" '+ ((tnm['code'][0]=="c")?"selected":"") +'>c</option>' +
        '    </select>' +
        '    <select name="t_1" id="t_1">' +
        '        <option value="'+ tnm_1 +'" '+ ((tnm['code'][1]=="")?"selected":"") +'>'+ tnm_1 +'</option>' +
        '    </select>' +
        '    <select name="t_2" id="t_2">' +
        '        <option value="" '+ ((tnm['code'][2]=="")?"selected":"") +'>(空)</option>' +
        '        <option value="X" '+ ((tnm['code'][2]=="X")?"selected":"") +'>X</option>' +
        '        <option value="is" '+ ((tnm['code'][2]=="is")?"selected":"") +'>is</option>' +
        '        <option value="0" '+ ((tnm['code'][2]=="0")?"selected":"") +'>0</option>' +
        '        <option value="1" '+ ((tnm['code'][2]=="1")?"selected":"") +'>1</option>' +
        '        <option value="2" '+ ((tnm['code'][2]=="2")?"selected":"") +'>2</option>' +
        '        <option value="3" '+ ((tnm['code'][2]=="3")?"selected":"") +'>3</option>' +
        '        <option value="4" '+ ((tnm['code'][2]=="4")?"selected":"") +'>4</option>' +
        '        <option value="5" '+ ((tnm['code'][2]=="5")?"selected":"") +'>5</option>' +
        '    </select>' +
        '    <select name="t_3" id="t_3">' +
        '        <option value="" '+ ((tnm['code'][3]=="")?"selected":"") +'>(空)</option>' +
        '        <option value="a" '+ ((tnm['code'][3]=="a")?"selected":"") +'>a</option>' +
        '        <option value="a1" '+ ((tnm['code'][3]=="a1")?"selected":"") +'>a1</option>' +
        '        <option value="a2" '+ ((tnm['code'][3]=="a2")?"selected":"") +'>a2</option>' +
        '        <option value="b" '+ ((tnm['code'][3]=="b")?"selected":"") +'>b</option>' +
        '        <option value="b1" '+ ((tnm['code'][3]=="b1")?"selected":"") +'>b1</option>' +
        '        <option value="b2" '+ ((tnm['code'][3]=="b2")?"selected":"") +'>b2</option>' +
        '        <option value="c" '+ ((tnm['code'][3]=="c")?"selected":"") +'>c</option>' +
        '        <option value="c1" '+ ((tnm['code'][3]=="c1")?"selected":"") +'>c1</option>' +
        '        <option value="c2" '+ ((tnm['code'][3]=="c2")?"selected":"") +'>c2</option>' +
        '        <option value="c3" '+ ((tnm['code'][3]=="c3")?"selected":"") +'>c3</option>' +
        '        <option value="d" '+ ((tnm['code'][3]=="d")?"selected":"") +'>d</option>' +
        '        <option value="e" '+ ((tnm['code'][3]=="e")?"selected":"") +'>e</option>' +
        '    </select>' +
        '    <select name="t_4" id="t_4">' +
        '        <option value="" '+ ((tnm['code'][4]=="")?"selected":"") +'>(空)</option>' +
        '        <option value="mi" '+ ((tnm['code'][4]=="mi")?"selected":"") +'>mi</option>' +
        '        <option value="Upper" '+ ((tnm['code'][4]=="Upper")?"selected":"") +'>Upper</option>' +
        '        <option value="Middle" '+ ((tnm['code'][4]=="Middle")?"selected":"") +'>Middle</option>' +
        '        <option value="Lower" '+ ((tnm['code'][4]=="Lower")?"selected":"") +'>Lower</option>' +
        '        <option value="High" '+ ((tnm['code'][4]=="High")?"selected":"") +'>High</option>' +
        '        <option value="Low" '+ ((tnm['code'][4]=="Low")?"selected":"") +'>Low</option>' +
        '        <option value="<10" '+ ((tnm['code'][4]=="<10")?"selected":"") +'>&lt;10</option>' +
        '        <option value=">=10,<20" '+ ((tnm['code'][4]==">=10,<20")?"selected":"") +'>&gt;=10,&lt;20</option>' +
        '        <option value="<20" '+ ((tnm['code'][4]=="<20")?"selected":"") +'>&lt;20</option>' +
        '        <option value=">=20" '+ ((tnm['code'][4]==">=20")?"selected":"") +'>&gt;=20</option>' +
        '        <option value="Any" '+ ((tnm['code'][4]=="Any")?"selected":"") +'>Any</option>' +
        '    </select>' +
        '    (<select name="t_5" id="t_5">' +
        '        <option value="" '+ ((tnm['code'][5]=="")?"selected":"") +'>(空)</option>' +
        '        <option value="DCIS" '+ ((tnm['code'][5]=="DCIS")?"selected":"") +'>DCIS</option>' +
        '        <option value="Paget" '+ ((tnm['code'][5]=="Paget")?"selected":"") +'>Paget</option>' +
        '        <option value="LCIS" '+ ((tnm['code'][5]=="LCIS")?"selected":"") +'>LCIS</option>' +
        '        <option value="mol+" '+ ((tnm['code'][5]=="mol+")?"selected":"") +'>mol+</option>' +
        '        <option value="mol-" '+ ((tnm['code'][5]=="mol-")?"selected":"") +'>mol-</option>' +
        '        <option value="i+" '+ ((tnm['code'][5]=="i+")?"selected":"") +'>i+</option>' +
        '        <option value="i-" '+ ((tnm['code'][5]=="i-")?"selected":"") +'>i-</option>' +
        '        <option value="l+" '+ ((tnm['code'][5]=="l+")?"selected":"") +'>l+</option>' +
        '        <option value="LAMN" '+ ((tnm['code'][5]=="LAMN")?"selected":"") +'>LAMN</option>' +
        '        <option value="0" '+ ((tnm['code'][5]=="0")?"selected":"") +'>0</option>' +
        '        <option value="1" '+ ((tnm['code'][5]=="1")?"selected":"") +'>1</option>' +
        '        <option value="2" '+ ((tnm['code'][5]=="2")?"selected":"") +'>2</option>' +
        '        <option value="Unknown" '+ ((tnm['code'][5]=="Unknown")?"selected":"") +'>Unknown</option>' +
        '        <option value="Low_risk" '+ ((tnm['code'][5]=="Low_risk")?"selected":"") +'>Low_risk</option>' +
        '        <option value="High_risk" '+ ((tnm['code'][5]=="High_risk")?"selected":"") +'>High_risk</option>' +
        '        <option value="Any" '+ ((tnm['code'][5]=="Any")?"selected":"") +'>Any</option>' +
        '        <option value="Positive" '+ ((tnm['code'][5]=="Positive")?"selected":"") +'>Positive</option>' +
        '        <option value="Negative" '+ ((tnm['code'][5]=="Negative")?"selected":"") +'>Negative</option>' +
        '    </select>)' +
        '</span>' +
        '<p> 说明 </p>' +
        '<span>' +
        '    <textarea rows="3" cols="50" name="t_desc" id="t_desc">'+ tnm['desc'] +'</textarea>' +
        '</span>' + 
        '<p> 排序权重 </p>' +
        '<span>' +
        '    <input type="text" name="t_weight" id="t_weight" value="'+ tnm['weight'] +'"/> <i>值越小越靠前</i>' +
        '</span>' +
        '<p> 置灰（不能点击）: ' +
        '    <input type="checkbox" name="t_grey" id="t_grey" ' + (((tnm.hasOwnProperty('grey'))?tnm['grey']==1:false)?'checked="checked"':'') + ' /> ' +
        '</p>' +
        '</div>';

    //console.log(dlgContentHTML);

    
    if ($("#dlgContentHTML").length>0){
        $('#t_0').val(tnm['code'][0]);
        $('#t_1').val(tnm['code'][1]);
        $('#t_2').val(tnm['code'][2]);
        $('#t_3').val(tnm['code'][3]);
        $('#t_4').val(tnm['code'][4]);
        $('#t_5').val(tnm['code'][5]);
        $('#t_desc').val(tnm['desc']);
        $('#t_weight').val(tnm['weight']);
        $("#t_grey").prop("checked", (tnm.hasOwnProperty('grey'))?tnm['grey']==1:false);
    }
    

    /* Now instead of making a prompt Dialog , use a Confirm Dialog */
    alertify.confirm2(dlgContentHTML).set('onok', function(closeevent, value) { 
        var t_0 = $('#t_0').val().trim();
        var t_1 = $('#t_1').val().trim();
        var t_2 = $('#t_2').val().trim();
        var t_3 = $('#t_3').val().trim();
        var t_4 = $('#t_4').val().trim();
        var t_5 = $('#t_5').val().trim();
        var t_desc = $('#t_desc').val().trim();
        var t_weight = $('#t_weight').val().trim();
        var t_grey = ($("#t_grey").prop("checked"))?1:0;

        if (isNaN(t_weight)){
            alertify.error('权重只能输入数字');
            return;
        }

        var div_html = tnm_html(title, tnm_1, tnm_num, t_0, t_1, t_2, t_3, t_4, t_5, t_desc, t_weight, t_grey);

        if (is_new)
            $('#'+tnm_1+'_list').append(div_html);
        else
            $('#'+tnm_1+'_'+tnm_num).replaceWith(div_html);

        tnm_rec[tnm_1][tnm_num] = {
            'code' : [t_0, t_1, t_2, t_3, t_4, t_5],
            'desc' : t_desc,
            'weight' : t_weight*1,  
            'grey' : t_grey,
        }

        alertify.success('已添加');

        history.go(-1);
                                 
    }).set('oncancel', function() {history.go(-1);}).set('title', title);

    return false;
}

function tnm_html(title, tnm_1, tnm_num, t_0, t_1, t_2, t_3, t_4, t_5, t_desc, t_weight, t_grey){
    // 修改 tnm_edit(title, tnm_1, tnm_num, false)
    var div_html = '<div class="start_from_left" id="'+ tnm_1 + '_' + tnm_num +'">' +
    '    <span><a href="#" onclick="tnm_edit(\''+title+'\',\''+tnm_1+'\','+tnm_num+',false)">'+ 
    t_0+t_1+t_2+t_3+t_4+((t_5.length==0)?'':'('+t_5+')') +'</a></span>' + 
    '    <span>&nbsp;('+ t_weight +')' + ((t_grey==1)?'(灰)':'') +'&nbsp;-&nbsp;' + highlight_text(t_desc) +'</span>' +
    '    <span>&nbsp;&nbsp;<a href="#" onclick="tnm_remove(\''+tnm_1+'\','+tnm_num+')">删除</a></span>'
    '</div>';

    return div_html;
}

function tnm_save(){
    var rule_id=$("#rule_id").val().trim();
    var tnm_name=$("#tnm_name").val().trim();
    var tnm_subname1=$("#tnm_subname1").val().trim();
    var tnm_subname2=$("#tnm_subname2").val().trim();
    var use_at=$("#use_at").val().trim();
    var weight=$("#weight").val().trim();
    var version=$("input[name='version']:checked").val();
    var available=$("input[name='available']:checked").val();
    var cancer_category=$('select[name=cancer_category]').val().trim();
    var node_question = $('#node_question').is(":checked");
    var ret_set = {'T':1, 'N':1, 'M':1};

    ret_set['G'] = ($('#ret_G').prop('checked'))?1:0;
    ret_set['L'] = ($('#ret_L').prop('checked'))?1:0;
    ret_set['S'] = ($('#ret_S').prop('checked'))?1:0;
    ret_set['Y'] = ($('#ret_Y').prop('checked'))?1:0;
    ret_set['PSA'] = ($('#ret_PSA').prop('checked'))?1:0;
    ret_set['HE'] = ($('#ret_HE').prop('checked'))?1:0;
    ret_set['RISK'] = ($('#ret_RISK').prop('checked'))?1:0;
    ret_set['HER2'] = ($('#ret_HER2').prop('checked'))?1:0;
    ret_set['ER'] = ($('#ret_ER').prop('checked'))?1:0;
    ret_set['PR'] = ($('#ret_PR').prop('checked'))?1:0;

    var rich_text = $('#summernote').summernote('code');
    $("#rich_text").val(rich_text);
    var t_memo = $('#summernote_t').summernote('code');
    $("#t_memo").val(t_memo);
    var n_memo = $('#summernote_n').summernote('code');
    $("#n_memo").val(n_memo);
    var m_memo = $('#summernote_m').summernote('code');
    $("#m_memo").val(m_memo);
    var g_memo = $('#summernote_g').summernote('code');
    $("#g_memo").val(g_memo);

    if (tnm_name.length==0){
        alertify.error("病种不能为空！");
        return false;
    }

    if (cancer_category.length==0){
        alertify.error("肿瘤类别不能为空！");
        return false;
    }

    $.ajax({
        type: "POST",
        url: "/plat/tnm_edit",
        async: true,
        timeout: 15000,
        data: {rule_id:rule_id,tnm_name:tnm_name,use_at:use_at,available:available,version:version,
            t_memo:t_memo,n_memo:n_memo,m_memo:m_memo,g_memo:g_memo,weight:weight,rich_text:rich_text,
            tnm_rec:JSON.stringify(tnm_rec),stage_rec:JSON.stringify(stage_rec),
            cancer_category:cancer_category,tnm_subname1:tnm_subname1,tnm_subname2:tnm_subname2,
            node_question:node_question,ret_set:JSON.stringify(ret_set)},
        dataType: "json",
        complete: function(xhr, textStatus)
        {
            if(xhr.status==200){
                var retJson = JSON.parse(xhr.responseText);
                if (retJson["ret"]==0){
                    alertify.alert("保存成功",retJson["msg"], function(){
                        //window.location.replace('/plat/tnm');
                        location.reload();
                    });
                }
                else{
                    alertify.alert("保存时出错",retJson["msg"], function(){
                    });
                    //alertify.error(retJson["msg"]);
                }
            }
            else{
                alertify.error("网络异常！请稍后再试");
            }
        }
    });

    return true;

}

function stage_remove(stage_num){
    alertify.confirm("请确认 ...", "确定要删除吗？",
        function(){
            $("#stage_"+stage_num).remove();
            stage_rec[stage_num]=null;
        },
        function(){
    });
}

function stage_copy(stage_num){
    alertify.confirm("请确认 ...", "确定要复制吗？",
        function(){
            var new_stage_num = stage_rec.length;
            stage_rec[new_stage_num] = JSON.parse(JSON.stringify(stage_rec[stage_num]));
            stage_rec[new_stage_num]['name'] += "(+)";
            var div_html = stage_html(new_stage_num, stage_rec[new_stage_num]);
            $('#stage_list').append(div_html);

            var back = ["#F78181","#FAAC58","#F7D358","#ACFA58","#2EFEF7","#58ACFA","#F781F3","#FE2E64","#FE2E64"];
            var rand = back[Math.floor(Math.random() * back.length)];
            $("#stage_"+stage_num).css("background-color", rand);
            $("#stage_"+new_stage_num).css("background-color", rand);
            alertify.success('已添加');
            history.go(-1);
        },
        function(){
    });
}


/* 参数： 标题， 主编码， tnm数据, 页面项目序号 */
function stage_edit(stage_num, is_new){
    var stage;

    if (is_new){
        stage = {
            'name' : '',
            'T'    : {'rule':'or', 'val':''},
            'N'    : {'rule':'or', 'val':''},
            'M'    : {'rule':'or', 'val':''},
            'G'    : {'rule':'or', 'val':''},
            'L'    : {'rule':'or', 'val':''},
            'S'    : {'rule':'or', 'val':''},
            'Y'    : {'rule':'or', 'val':''},
            'PSA'  : {'rule':'or', 'val':''},
            'HE'   : {'rule':'or', 'val':''},
            'RISK'   : {'rule':'or', 'val':''},
            'HER2'   : {'rule':'or', 'val':''},
            'ER'   : {'rule':'or', 'val':''},
            'PR'   : {'rule':'or', 'val':''},
            'desc' : '',
            'weight' : 999,
        }
    }
    else{
        stage = stage_rec[stage_num];
        if (!stage.hasOwnProperty('desc')) stage['desc']='';
    }

    var dlgContentHTML = '<div id="dlgContentHTML">' + 
        '    <div><span style="width:40px;display:inline-block;">分期</span>' +
        '        <input type="text" id="stage_name" size="20" value="'+stage['name']+'" /></div>' +
        '    <div><span style="width:40px;display:inline-block;">T</span>' +
        '        <input type="text" id="T_names" size="30" placeholder="使用逗号分隔多个项目" value="'+ stage['T']['val'] +'" />' +
        '        <input type="radio" name="T_and_or" id="T_or"  value="or"  '+ ((stage['T']['rule']!="any")?"checked":"") +  '/> 或' +
        '        <input type="radio" name="T_and_or" id="T_any" value="any" '+ ((stage['T']['rule']=="any")?"checked":"") + '/> Any' +
        '    </div>' +
        '    <div><span style="width:40px;display:inline-block;">N</span>' +
        '        <input type="text" id="N_names" size="30" placeholder="使用逗号分隔多个项目" value="'+ stage['N']['val'] +'" />' +
        '        <input type="radio" name="N_and_or" value="or"  '+ ((stage['N']['rule']!="any")?"checked":"") +  '/> 或' +
        '        <input type="radio" name="N_and_or" value="any" '+ ((stage['N']['rule']=="any")?"checked":"") + '/> Any' +
        '    </div>' +
        '    <div><span style="width:40px;display:inline-block;">M</span>' +
        '        <input type="text" id="M_names" size="30" placeholder="使用逗号分隔多个项目" value="'+ stage['M']['val'] +'" />' +
        '        <input type="radio" name="M_and_or" value="or"  '+ ((stage['M']['rule']!="any")?"checked":"") +  '/> 或' +
        '        <input type="radio" name="M_and_or" value="any" '+ ((stage['M']['rule']=="any")?"checked":"") + '/> Any' +
        '    </div>' +
        '    <div><span style="width:40px;display:inline-block;">G</span>' +
        '        <input type="text" id="G_names" size="30" placeholder="使用逗号分隔多个项目" value="'+ stage['G']['val'] +'" />' +
        '        <input type="radio" name="G_and_or" value="or"  '+ ((stage['G']['rule']!="any")?"checked":"") +  '/> 或' +
        '        <input type="radio" name="G_and_or" value="any" '+ ((stage['G']['rule']=="any")?"checked":"") + '/> Any' +
        '    </div>' +
        '    <div><span style="width:40px;display:inline-block;">L</span>' +
        '        <input type="text" id="L_names" size="30" placeholder="使用逗号分隔多个项目" value="'+ stage['L']['val'] +'" />' +
        '        <input type="radio" name="L_and_or" value="or"  '+ ((stage['L']['rule']!="any")?"checked":"") +  '/> 或' +
        '        <input type="radio" name="L_and_or" value="any" '+ ((stage['L']['rule']=="any")?"checked":"") + '/> Any' +
        '    </div>' +
        '    <div><span style="width:40px;display:inline-block;">S</span>' +
        '        <input type="text" id="S_names" size="30" placeholder="使用逗号分隔多个项目" value="'+ stage['S']['val'] +'" />' +
        '        <input type="radio" name="S_and_or" value="or"  '+ ((stage['S']['rule']!="any")?"checked":"") +  '/> 或' +
        '        <input type="radio" name="S_and_or" value="any" '+ ((stage['S']['rule']=="any")?"checked":"") + '/> Any' +
        '    </div>' +
        '    <div><span style="width:40px;display:inline-block;">Y</span>' +
        '        <input type="text" id="Y_names" size="30" placeholder="使用逗号分隔多个项目" value="'+ stage['Y']['val'] +'" />' +
        '        <input type="radio" name="Y_and_or" value="or"  '+ ((stage['Y']['rule']!="any")?"checked":"") +  '/> 或' +
        '        <input type="radio" name="Y_and_or" value="any" '+ ((stage['Y']['rule']=="any")?"checked":"") + '/> Any' +
        '    </div>' +
        '    <div><span style="width:40px;display:inline-block;">PSA</span>' +
        '        <input type="text" id="PSA_names" size="30" placeholder="使用逗号分隔多个项目" value="'+ stage['PSA']['val'] +'" />' +
        '        <input type="radio" name="PSA_and_or" value="or"  '+ ((stage['PSA']['rule']!="any")?"checked":"") +  '/> 或' +
        '        <input type="radio" name="PSA_and_or" value="any" '+ ((stage['PSA']['rule']=="any")?"checked":"") + '/> Any' +
        '    </div>' +
        '    <div><span style="width:40px;display:inline-block;">HE</span>' +
        '        <input type="text" id="HE_names" size="30" placeholder="使用逗号分隔多个项目" value="'+ stage['HE']['val'] +'" />' +
        '        <input type="radio" name="HE_and_or" value="or"  '+ ((stage['HE']['rule']!="any")?"checked":"") +  '/> 或' +
        '        <input type="radio" name="HE_and_or" value="any" '+ ((stage['HE']['rule']=="any")?"checked":"") + '/> Any' +
        '    </div>' +
        '    <div><span style="width:40px;display:inline-block;">RISK</span>' +
        '        <input type="text" id="RISK_names" size="30" placeholder="使用逗号分隔多个项目" value="'+ stage['RISK']['val'] +'" />' +
        '        <input type="radio" name="RISK_and_or" value="or"  '+ ((stage['RISK']['rule']!="any")?"checked":"") +  '/> 或' +
        '        <input type="radio" name="RISK_and_or" value="any" '+ ((stage['RISK']['rule']=="any")?"checked":"") + '/> Any' +
        '    </div>' +

        '    <div><span style="width:40px;display:inline-block;">HER2</span>' +
        '        <input type="text" id="HER2_names" size="30" placeholder="使用逗号分隔多个项目" value="'+ stage['HER2']['val'] +'" />' +
        '        <input type="radio" name="HER2_and_or" value="or"  '+ ((stage['HER2']['rule']!="any")?"checked":"") +  '/> 或' +
        '        <input type="radio" name="HER2_and_or" value="any" '+ ((stage['HER2']['rule']=="any")?"checked":"") + '/> Any' +
        '    </div>' +
        '    <div><span style="width:40px;display:inline-block;">ER</span>' +
        '        <input type="text" id="ER_names" size="30" placeholder="使用逗号分隔多个项目" value="'+ stage['ER']['val'] +'" />' +
        '        <input type="radio" name="ER_and_or" value="or"  '+ ((stage['ER']['rule']!="any")?"checked":"") +  '/> 或' +
        '        <input type="radio" name="ER_and_or" value="any" '+ ((stage['ER']['rule']=="any")?"checked":"") + '/> Any' +
        '    </div>' +
        '    <div><span style="width:40px;display:inline-block;">PR</span>' +
        '        <input type="text" id="PR_names" size="30" placeholder="使用逗号分隔多个项目" value="'+ stage['PR']['val'] +'" />' +
        '        <input type="radio" name="PR_and_or" value="or"  '+ ((stage['PR']['rule']!="any")?"checked":"") +  '/> 或' +
        '        <input type="radio" name="PR_and_or" value="any" '+ ((stage['PR']['rule']=="any")?"checked":"") + '/> Any' +
        '    </div>' +

        '    <p> 文字说明：' +
        '    <div>' +
        '    <textarea rows="4" cols="50" name="stage_desc" id="stage_desc" ' +
        '        placeholder="跳转到页面“@(页面编码)”； 跳转到网页链接“@(网址链接)”或“@(网页标题|网址链接)”；注释使用方括号 [] 括起来，内填注释编码">'+ stage['desc'] +'</textarea>' +
        '    </div></p>' + 
        '    <p>排序权重 ' +
        '        <input type="text" name="stage_weight" id="stage_weight" value="'+ stage['weight'] +'"/> <i>值越小越靠前</i>' +
        '    </p>' +
        '</div>';

    //console.log(dlgContentHTML);
    //console.log(stage);

    if ($("#dlgContentHTML").length>0){
        $('#stage_name').val(stage['name']);
        $('input[type="radio"][name="T_and_or"][value="'+stage['T']['rule']+'"]').prop('checked', 'checked');
        $('#T_names').val(stage['T']['val']);
        $('input[type="radio"][name="N_and_or"][value="'+stage['N']['rule']+'"]').prop('checked', 'checked');
        $('#N_names').val(stage['N']['val']);
        $('input[type="radio"][name="M_and_or"][value="'+stage['M']['rule']+'"]').prop('checked', 'checked');
        $('#M_names').val(stage['M']['val']);
        $('input[type="radio"][name="G_and_or"][value="'+stage['G']['rule']+'"]').prop('checked', 'checked');
        $('#G_names').val(stage['G']['val']);
        $('input[type="radio"][name="L_and_or"][value="'+stage['L']['rule']+'"]').prop('checked', 'checked');
        $('#L_names').val(stage['L']['val']);
        $('input[type="radio"][name="S_and_or"][value="'+stage['S']['rule']+'"]').prop('checked', 'checked');
        $('#S_names').val(stage['S']['val']);
        $('input[type="radio"][name="Y_and_or"][value="'+stage['Y']['rule']+'"]').prop('checked', 'checked');
        $('#Y_names').val(stage['Y']['val']);
        $('input[type="radio"][name="PSA_and_or"][value="'+stage['PSA']['rule']+'"]').prop('checked', 'checked');
        $('#PSA_names').val(stage['PSA']['val']);
        $('input[type="radio"][name="HE_and_or"][value="'+stage['HE']['rule']+'"]').prop('checked', 'checked');
        $('#HE_names').val(stage['HE']['val']);
        $('input[type="radio"][name="RISK_and_or"][value="'+stage['RISK']['rule']+'"]').prop('checked', 'checked');
        $('#RISK_names').val(stage['RISK']['val']);

        $('input[type="radio"][name="HER2_and_or"][value="'+stage['HER2']['rule']+'"]').prop('checked', 'checked');
        $('#HER2_names').val(stage['HER2']['val']);
        $('input[type="radio"][name="ER_and_or"][value="'+stage['ER']['rule']+'"]').prop('checked', 'checked');
        $('#ER_names').val(stage['ER']['val']);
        $('input[type="radio"][name="PR_and_or"][value="'+stage['PR']['rule']+'"]').prop('checked', 'checked');
        $('#PR_names').val(stage['PR']['val']);

        $('#stage_weight').val(stage['weight']);
        $('#stage_desc').val(stage['desc']);
    }


    /* Now instead of making a prompt Dialog , use a Confirm Dialog */
    alertify.confirm2(dlgContentHTML).set('onok', function(closeevent, value) { 

        var div_html;

        stage_rec[stage_num] = {
            'name' : $('#stage_name').val().trim(),
            'T'    : {'rule':$('input[type="radio"][name="T_and_or"]:checked').val(), 'val':$('#T_names').val()},
            'N'    : {'rule':$('input[type="radio"][name="N_and_or"]:checked').val(), 'val':$('#N_names').val()},
            'M'    : {'rule':$('input[type="radio"][name="M_and_or"]:checked').val(), 'val':$('#M_names').val()},
            'G'    : {'rule':$('input[type="radio"][name="G_and_or"]:checked').val(), 'val':$('#G_names').val()},
            'L'    : {'rule':$('input[type="radio"][name="L_and_or"]:checked').val(), 'val':$('#L_names').val()},
            'S'    : {'rule':$('input[type="radio"][name="S_and_or"]:checked').val(), 'val':$('#S_names').val()},
            'Y'    : {'rule':$('input[type="radio"][name="Y_and_or"]:checked').val(), 'val':$('#Y_names').val()},
            'PSA'  : {'rule':$('input[type="radio"][name="PSA_and_or"]:checked').val(), 'val':$('#PSA_names').val()},
            'HE'   : {'rule':$('input[type="radio"][name="HE_and_or"]:checked').val(), 'val':$('#HE_names').val()},
            'RISK' : {'rule':$('input[type="radio"][name="RISK_and_or"]:checked').val(), 'val':$('#RISK_names').val()},
            'HER2'  : {'rule':$('input[type="radio"][name="HER2_and_or"]:checked').val(), 'val':$('#HER2_names').val()},
            'ER'  : {'rule':$('input[type="radio"][name="ER_and_or"]:checked').val(), 'val':$('#ER_names').val()},
            'PR'  : {'rule':$('input[type="radio"][name="PR_and_or"]:checked').val(), 'val':$('#PR_names').val()},
            'weight' : $('#stage_weight').val().trim()*1,
            'desc' : $('#stage_desc').val().trim(),
        }

        if (stage_rec[stage_num]['name'].length==0){
            alertify.warning('分期不能为空');
            return false;
        }

        div_html = stage_html(stage_num, stage_rec[stage_num]);

        if (is_new)
            $('#stage_list').append(div_html);
        else
            $('#stage_'+stage_num).replaceWith(div_html);

        alertify.success('已添加');

        history.go(-1);
       
    }).set('oncancel', function() {history.go(-1);}).set('title', '分期数据');

    return false;
}

function and_or_any(s){
    switch (s){
        case 'and':
        case 'or':
            return '';
        case 'any':
            return '(ANY)';
        default:
            return '';
    }
}

function stage_html(stage_num, stage){
    var div_html = '    <tr id="stage_' + stage_num +'">' +
    '    <td><a href="#" onclick="stage_edit('+stage_num+',false)">'+stage['name']+'</a> ('+stage['weight']+')' +
    ((stage.hasOwnProperty('desc'))?((stage['desc'].length>0)?'&nbsp;<img height="15" src="/static/image/link.png"/>':''):'')+'</td>' +
    '    <td><span style="color:#f30">'+and_or_any(stage['T']['rule'])+'</span> '+stage['T']['val']+'</td>' +
    '    <td><span style="color:#f30">'+and_or_any(stage['N']['rule'])+'</span> '+stage['N']['val']+'</td>' +
    '    <td><span style="color:#f30">'+and_or_any(stage['M']['rule'])+'</span> '+stage['M']['val']+'</td>' +
    '    <td><span style="color:#f30">'+and_or_any(stage['G']['rule'])+'</span> '+stage['G']['val']+'</td>' +
    '    <td><span style="color:#f30">'+and_or_any(stage['L']['rule'])+'</span> '+stage['L']['val']+'</td>' +
    '    <td><span style="color:#f30">'+and_or_any(stage['S']['rule'])+'</span> '+stage['S']['val']+'</td>' +
    '    <td><span style="color:#f30">'+and_or_any(stage['Y']['rule'])+'</span> '+stage['Y']['val']+'</td>' +
    '    <td><span style="color:#f30">'+and_or_any(stage['PSA']['rule'])+'</span> '+stage['PSA']['val']+'</td>' +
    '    <td><span style="color:#f30">'+and_or_any(stage['HE']['rule'])+'</span> '+stage['HE']['val']+'</td>' +
    '    <td><span style="color:#f30">'+and_or_any(stage['RISK']['rule'])+'</span> '+stage['RISK']['val']+'</td>' +
    '    <td><span style="color:#f30">'+and_or_any(stage['HER2']['rule'])+'</span> '+stage['HER2']['val']+'</td>' +
    '    <td><span style="color:#f30">'+and_or_any(stage['ER']['rule'])+'</span> '+stage['ER']['val']+'</td>' +
    '    <td><span style="color:#f30">'+and_or_any(stage['PR']['rule'])+'</span> '+stage['PR']['val']+'</td>' +
    '    <td><a href="#" onclick="stage_copy('+stage_num+')">复制</a>&nbsp;&nbsp' +
    '        <a href="#" onclick="stage_remove('+stage_num+')">删除</a></td>' +
    '</tr>';

    return div_html;
}

/**
 * Confirm dialog object
 *
 *  alertify.confirm(message);
 *  alertify.confirm(message, onok);
 *  alertify.confirm(message, onok, oncancel);
 *  alertify.confirm(title, message, onok, oncancel);
 */
alertify.dialog('confirm2', function () {

    var autoConfirm = {
        timer: null,
        index: null,
        text: null,
        duration: null,
        task: function (event, self) {
            if (self.isOpen()) {
                self.__internal.buttons[autoConfirm.index].element.innerHTML = autoConfirm.text + ' (&#8207;' + autoConfirm.duration + '&#8207;) ';
                autoConfirm.duration -= 1;
                if (autoConfirm.duration === -1) {
                    clearAutoConfirm(self);
                    var button = self.__internal.buttons[autoConfirm.index];
                    var closeEvent = createCloseEvent(autoConfirm.index, button);

                    if (typeof self.callback === 'function') {
                        self.callback.apply(self, [closeEvent]);
                    }
                    //close the dialog.
                    if (closeEvent.close !== false) {
                        self.close();
                    }
                }
            } else {
                clearAutoConfirm(self);
            }
        }
    };

    function clearAutoConfirm(self) {
        if (autoConfirm.timer !== null) {
            clearInterval(autoConfirm.timer);
            autoConfirm.timer = null;
            self.__internal.buttons[autoConfirm.index].element.innerHTML = autoConfirm.text;
        }
    }

    function startAutoConfirm(self, index, duration) {
        clearAutoConfirm(self);
        autoConfirm.duration = duration;
        autoConfirm.index = index;
        autoConfirm.text = self.__internal.buttons[index].element.innerHTML;
        autoConfirm.timer = setInterval(delegate(self, autoConfirm.task), 1000);
        autoConfirm.task(null, self);
    }


    return {
        main: function (_title, _message, _onok, _oncancel) {
            var title, message, onok, oncancel;
            switch (arguments.length) {
            case 1:
                message = _title;
                break;
            case 2:
                message = _title;
                onok = _message;
                break;
            case 3:
                message = _title;
                onok = _message;
                oncancel = _onok;
                break;
            case 4:
                title = _title;
                message = _message;
                onok = _onok;
                oncancel = _oncancel;
                break;
            }
            this.set('title', title);
            this.set('message', message);
            this.set('onok', onok);
            this.set('oncancel', oncancel);
            return this;
        },
        setup: function () {
            return {
                buttons: [
                    {
                        text: alertify.defaults.glossary.ok,
                        key: -1, //keys.ENTER,
                        className: alertify.defaults.theme.ok,
                    },
                    {
                        text: alertify.defaults.glossary.cancel,
                        key: 27, //keys.ESC,
                        invokeOnClose: true,
                        className: alertify.defaults.theme.cancel,
                    }
                ],
                focus: {
                    element: 0,
                    select: false
                },
                options: {
                    maximizable: false,
                    resizable: false
                }
            };
        },
        build: function () {
            //nothing
        },
        prepare: function () {
            //nothing
        },
        setMessage: function (message) {
            this.setContent(message);
        },
        settings: {
            message: null,
            labels: null,
            onok: null,
            oncancel: null,
            defaultFocus: null,
            reverseButtons: null,
        },
        settingUpdated: function (key, oldValue, newValue) {
            switch (key) {
            case 'message':
                this.setMessage(newValue);
                break;
            case 'labels':
                if ('ok' in newValue && this.__internal.buttons[0].element) {
                    this.__internal.buttons[0].text = newValue.ok;
                    this.__internal.buttons[0].element.innerHTML = newValue.ok;
                }
                if ('cancel' in newValue && this.__internal.buttons[1].element) {
                    this.__internal.buttons[1].text = newValue.cancel;
                    this.__internal.buttons[1].element.innerHTML = newValue.cancel;
                }
                break;
            case 'reverseButtons':
                if (newValue === true) {
                    this.elements.buttons.primary.appendChild(this.__internal.buttons[0].element);
                } else {
                    this.elements.buttons.primary.appendChild(this.__internal.buttons[1].element);
                }
                break;
            case 'defaultFocus':
                this.__internal.focus.element = newValue === 'ok' ? 0 : 1;
                break;
            }
        },
        callback: function (closeEvent) {
            clearAutoConfirm(this);
            var returnValue;
            switch (closeEvent.index) {
            case 0:
                if (typeof this.get('onok') === 'function') {
                    returnValue = this.get('onok').call(this, closeEvent);
                    if (typeof returnValue !== 'undefined') {
                        closeEvent.cancel = !returnValue;
                    }
                }
                break;
            case 1:
                if (typeof this.get('oncancel') === 'function') {
                    returnValue = this.get('oncancel').call(this, closeEvent);
                    if (typeof returnValue !== 'undefined') {
                        closeEvent.cancel = !returnValue;
                    }
                }
                break;
            }
        },
        autoOk: function (duration) {
            startAutoConfirm(this, 0, duration);
            return this;
        },
        autoCancel: function (duration) {
            startAutoConfirm(this, 1, duration);
            return this;
        }
    };
});




