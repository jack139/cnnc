var cache_note={};

/* convert plain text to html */
function text2HTML(text) {
    // 1: Plain Text Search
    var text = text.replace(/&/g, "&amp;").
    replace(/</g, "&lt;").
    replace(/>/g, "&gt;");

    // 2: Line Breaks
    text = text.replace(/\r\n?|\n/g, "<br>");

    // 3: Paragraphs
    text = text.replace(/<br>\s*<br>/g, "</p><p>");

    // 替换跳转页面
    text = text.replace(/@[\w-.#]+/g, function($0){ 
        var page_code=$0.substr(1);
        return " <span class='bg-success'> <a href='/ui/doct?page_code="+page_code.replace('#','%23')+"'>"+page_code+"</a></span> ";
    });

    // 替换索引
    text = text.replace(/\[[\s\w-*#§¶†‡•Ü|]+\]/g, function($0){ 
        var note_code=$0.substr(1,$0.length-2);
        var p = note_code.lastIndexOf('-');
        return " <sup class='bg-warning'><a onclick='note_click(\""+note_code+"\")' href='#'>["+note_code.substr(p+1).replace('#','%23')+"]</a></sup> ";
    });

    // 4: Wrap in Paragraph Tags
    text = "<p>" + text + "</p>";

    return text;
}

/* filter note and @*/
function text2filter(text) {
    // 过滤跳转页面的@
    text = text.replace(/@[\w-.#]+/g, function($0){ return page_code=$0.substr(1); });

    // 过滤索引
    text = text.replace(/\[[\s\w-*#§¶†‡•Ü|]+\]/g, function($0){ return ""; });

    return text;
}


/* convert plain text to html */
function filterNote(text) {

    // 替换跳转页面
    text = text.replace(/@[\w-.#]+/g, function($0){ 
        var page_code=$0.substr(1);
        return " <span class='bg-success'> <a href='/ui/doct?page_code="+page_code.replace('#','%23')+"'>"+page_code+"</a></span> ";
    });

    // 替换索引
    text = text.replace(/\[[\s\w-*#§¶†‡•Ü|]+\]/g, function($0){ 
        var note_code=$0.substr(1,$0.length-2);
        var p = note_code.lastIndexOf('-');
        return " <sup class='bg-warning'><a onclick='note_click(\""+note_code+"\")' href='#'>["+note_code.substr(p+1).replace('#','%23')+"]</a></sup> ";
    });

    return text;
}

/* 处理和显示注释 */

function query_note(note_code){

    $.ajax({
        type: "POST",
        url: "/ui/node_note",
        async: true, 
        timeout: 15000,
        data: {note_code:note_code},
        dataType: "json",
        complete: function(xhr, textStatus)
        {
            if(xhr.status==200){
                var retJson = JSON.parse(xhr.responseText);
                if (retJson["ret"]==0){
                    cache_note[retJson["data"]["note_code"]] = retJson["data"]["content"]; //缓存note内容
                    $("#node_note").html(text2HTML(retJson["data"]["content"]));
                }
                else{
                    alertify.error('获取数据失败：'+retJson["msg"]); 
                }
            }
            else{
                alertify.error('网络异常!'); 
            }

        }
    });
}

function note_click(note_code){
    var dlgContentHTML = '<div id="dlgContentHTML">'+
        '<div id="node_note"></div>'+ 
        '</div>';

    alertify.alert(dlgContentHTML).set('onok', function(closeevent, value) { 
        history.go(-1);
    }).set('title',"注释 "+note_code);

    note_code = note_code.toUpperCase();

    if (cache_note.hasOwnProperty(note_code)){
        var note_text = cache_note[note_code];
        if ($("#dlgContentHTML").length>0) {
            $('#node_note').html(text2HTML(note_text));
        }
    }
    else{
        if ($("#dlgContentHTML").length>0) 
            $('#node_note').text("");
        query_note(note_code);
    }

    return false;
}



// text = "abc[BINV-2-¶†]ghi[BINS_1#1]1111"
// text.replace(/\[[\s\w-*#§¶†‡|]+\]/g, function($0){ return "<a href='"+$0.substr(1,$0.length-2)+"'>"+$0+"</a>"; })
// text="见局部@BINV-2和@BINV-3 )"
// text.replace(/@[\w-.]+/g, function($0){ return "'"+$0+"'"; })




function wx_interface(interface, parameter, todo_func){ /* parameter is dict */
    $.ajax({
        type: "POST",
        url: "/wx/"+interface,
        async: true, 
        timeout: 15000,
        data: parameter,
        dataType: "json",
        complete: function(xhr, textStatus)
        {
            if(xhr.status==200){
                var retJson = JSON.parse(xhr.responseText);
                if (retJson["ret"]==0){
                    todo_func(retJson["data"]);
                }
                else{
                    alertify.error('获取数据失败：'+retJson["msg"]); 
                }
            }
            else{
                alertify.error('网络异常!'); 
            }
        }
    });
}


function Node(text, pos_x, pos_y, node_id, node_prop, node_weight, node_question){
    this.text_long = this.text_short = text;
    this.text_status = -1; /* 0- short , 1- long , -1 不需展开*/
    this.x = pos_x;
    this.y = pos_y;
    this.node_id = node_id;
    this.node_prop = node_prop;
    this.node_question = node_question;
    this.node_weight = node_weight;
    this.node_width = 200;

    var max_char = 100;

    if (text.trim()=='*' || text.trim()=='+' || text.trim()=='0') {  // 虚节点
        if (text.trim()=='0') { 
            this.text_long = this.text_short = '起\n始\n节\n点'; 
            this.node_width = 45;
        }
    }
    else {
        if (text.length>max_char){
            this.text_status = 0;
            this.text_short = text.substr(0,max_char) + " ..."; 
        }
    }

    this.content_html = function(){
        var div_html = "";
        if (this.text_status==-1){
            div_html += text2HTML(this.text_long);
        }
        else if (this.text_status==0){
            div_html += text2HTML(this.text_short);
            div_html += "<button onclick=\"node_dict['"+this.node_id+"'].more_click(1);\">展开>></button>";
        }
        else{
            div_html += text2HTML(this.text_long);
            div_html += "<button onclick=\"node_dict['"+this.node_id+"'].more_click(0);\">收起<<</button>";
        }
        return div_html;
    };

    this.node_html = function(){
        return '<div id="'+this.node_id+'" class="draggable" style="position: absolute; left: '
            + this.x +'px; top: '+ this.y +'px; width: '+ this.node_width +'px;">' + this.content_html() + '</div>';
    };

    this.position = function(x, y){
        var div = $("#"+this.node_id);
        this.x = x;
        this.y = y;
        if (div.length>0){
            $("#"+this.node_id).css({top: y, left: x});
        }
    };

    this.appendToPaper = function(){
        var div = $("#"+this.node_id);
        if (div.length==0){
            $("#paper").append(this.node_html()); /*  生成节点 */
            
            var e = $("#"+this.node_id);

            e.touch();

            e.on('doubleTap',function(e){
                //alert("touch");
                element_touch(this.id);
            });
            
        }
    };

    this.getBBox =function(){
        var div = $("#"+this.node_id);
        if (div.length==0){
            this.appendToPaper();
            div = $("#"+this.node_id);
        }

        var p = div.position();
        return {
            x : p.left,
            y : p.top,
            width  : div.width(),
            height : div.height(),
        }
    };

    this.more_click = function(status){
        var div = $("#"+this.node_id);
        if (div.length==0) return;
        this.text_status = status;
        $("#"+this.node_id).html(this.content_html());
        $('.draggable').connections('update'); /* 刷新连线 */
    };
}
