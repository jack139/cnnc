var cache_note={};

/* convert plain text to html */
function text2HTML(text) {
    return text2HTML0(text, "", "", true, false);
}

function text2HTML0(text, tnm_code, tnm_name, wrap_para, is_grey) {
    var session_id = $("#session_id").val();
    
    // 1: Plain Text Search
    var text = text.replace(/&/g, "&amp;").
    replace(/</g, "&lt;").
    replace(/>/g, "&gt;");

    // 2: Line Breaks
    text = text.replace(/\r\n?|\n/g, "<br>");

    // 3: Paragraphs
    text = text.replace(/<br>\s*<br>/g, "</p><p>");

    // 替换跳转页面 有页面代码
    text = text.replace(/@\([\w-.#Ü]+\)/g, function($0){ 
        var page_code=$0.substr(1);
        return " <span class='jump_color'> <a href='/wx/doct_init?session_id="+session_id+"&page_code="+page_code.substr(1,page_code.length-2).replace('#','%23')+"'>"+page_code+"</a></span> ";
    });

    // 替换跳转页面 有链接
    text = text.replace(/@\((https:\/\/|http:\/\/).*?\)/g, function($0){ 
        var page_code=$0.substr(1);
        return " <span class='jump_color'> <a href='"+page_code.substr(1,page_code.length-2)+"'>"+page_code+"</a></span> ";
    });

    // 替换跳转页面 有 页面说明|链接
    text = text.replace(/@\(.*?\|(https:\/\/|http:\/\/).*?\)/g, function($0){ 
        var page_code=$0.substr(1);
        page_code = page_code.substr(1,page_code.length-2).split("|");
        return " <span class='jump_color'> <a href='"+page_code[1]+"'>"+page_code[0]+"</a></span> ";
    });

    // 替换索引
    text = text.replace(/\[[\s\w-*#§¶†‡•Ü|]+\]/g, function($0){ 
        var note_code=$0.substr(1,$0.length-2);
        var p = note_code.lastIndexOf('-');
        return " <sup class='jump_color'><a onclick='note_click(\""+note_code+"\")' href='#'>["+note_code.substr(p+1).replace('#','%23')+"]</a></sup> ";
    });

    // 替换tnm快捷点击
    text = text.replace(/\{.*?\}/g, function($0){ 
        var page_code=$0.substr(1,$0.length-2);
        return " <span class='jump_color2'><a onclick='select_click(\""+tnm_code+"\",\""+tnm_name+"\")' href='#'>"+page_code+"</a></span> ";
    });

    // 4: Wrap in Paragraph Tags
    if (wrap_para) 
        text = "<p style='"+ ((is_grey)?"color:grey;":"") +"'>" + text + "</p>";

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
    var session_id = $("#session_id").val();

    // 替换跳转页面
    text = text.replace(/@[\w-.#]+/g, function($0){ 
        var page_code=$0.substr(1);
        return " <span class='jump_color'> <a href='/wx/doct_init?session_id="+session_id+"&page_code="+page_code.replace('#','%23')+"'>"+page_code+"</a></span> ";
    });

    // 替换索引
    text = text.replace(/\[[\s\w-*#§¶†‡•Ü|]+\]/g, function($0){ 
        var note_code=$0.substr(1,$0.length-2);
        var p = note_code.lastIndexOf('-');
        return " <sup class='jump_color'><a onclick='note_click(\""+note_code+"\")' href='#'>["+note_code.substr(p+1).replace('#','%23')+"]</a></sup> ";
    });

    return text;
}

/* 处理和显示注释 */

function query_note(note_code){

    var session_id = $("#session_id").val();
    var version = $("#version").val();

    wx_interface(
        "node_note",
        {
            session_id : session_id,
            note_code  : note_code,
            version    : version,
        },
        function(data){
            cache_note[data["note_code"]] = data["content"]; //缓存note内容
            $("#note_text").html(text2HTML(data["content"]));
        }
    );
}

function note_click(note_code){
    $("#note_title").text("注释 "+note_code);

    note_code = note_code.toUpperCase();

    if (cache_note.hasOwnProperty(note_code)){
        var note_text = cache_note[note_code];
        $("#note_text").html(text2HTML(note_text));
    }
    else{
        $('#note_text').html("");
        query_note(note_code);
    }

    $(".sidebar.bottom").trigger("sidebar:open", [{ speed: 300 }]);

    event.stopPropagation();
    event.preventDefault();

    TDAPP.onEvent("点击注释", note_code);

    return false;
}


function select_click(tnm_code, tnm_name){
    $.each(tnm_data['tnm'][tnm_name], function(index, value){
        var t = value['code'];
        var code = t[0]+t[1]+t[2]+t[3]+t[4];
        code += (t[5].length==0)?'':'('+t[5]+')'; 

        if (code==tnm_code){
            user_select[tnm_name] = code;

            var text = code; // + '：' + value['desc'];
            text = text.replace(/\r\n?|\n/g, "");
            var div_html = text2HTML0(text, code, tnm_name, false, false);
            div_html += "<span class='jump_color3'><a href='#' onclick='open_tnm(\""+tnm_name+"\")'>重新选择</a></span>"
            $("#nodediv_"+tnm_name+"_bar_text").text("");
            $("#nodediv_"+tnm_name+"_title").html(div_html);
            $("#nodediv_"+tnm_name+"_tnm").hide();
            $("#nodediv_"+tnm_name+"_memo").hide();
            //check_next_tnm(tnm_code, tnm_name);
            check_tnm_status();
            return false;
        }
    });
    return false;
}

function check_next_tnm(tnm_code, tnm_name){
        var session_id = $("#session_id").val();
        var page_id = $("#page_id").val();

        wx_interface(
            "tnm_check",
            {
                session_id : session_id,
                page_id    : page_id,
                tnm        : JSON.stringify({'tnm_name':tnm_name, 'tnm_code':tnm_code}),
            },
            function(data){
                console.log(data);
            }
        );
}

function open_tnm(tnm_name){
    $("#nodediv_"+tnm_name+"_tnm").show();
    $("#nodediv_"+tnm_name+"_memo").show();
    return false;
}

/*
// text = "abc[BINV-2-¶†]ghi[BINS_1#1]1111"
// text.replace(/\[[\s\w-*#§¶†‡|]+\]/g, function($0){ return "<a href='"+$0.substr(1,$0.length-2)+"'>"+$0+"</a>"; })
// text="见局部@BINV-2和@BINV-3 )"
// text.replace(/@[\w-.]+/g, function($0){ return "'"+$0+"'"; })
*/


function wx_interface(interface2, parameter2, todo_func){  /* parameter2 is dict */
    $(".floatLayer").show();

    $.ajax({
        type: "POST",
        url: "/wx/"+interface2,
        async: true, 
        timeout: 15000,
        data: parameter2,
        dataType: "json",
        complete: function(xhr, textStatus)
        {
            if(xhr.status==200){
                var retJson = JSON.parse(xhr.responseText);
                if (retJson["ret"]==0){
                    todo_func(retJson["data"]);
                }
                else{
                    alertify.warning(retJson["msg"]);
                    TDAPP.onEvent("接口调用", '获取数据失败:'+interface2+':'+retJson["msg"], parameter2); 
                }
            }
            else{
                alertify.error('网络异常!'); 
                TDAPP.onEvent("接口调用", "网络异常:"+interface2+" "+xhr.status, parameter2);
            }

            $(".floatLayer").hide();
        }
    });
    
    TDAPP.onEvent("接口调用", interface2); 
}


function Node(node_data, tnm_name, node_type, page_id){
    this.node_data = node_data; /* tnm_data['tnm']['T'] or tnm_data['t_memo7 '] */
    this.node_id = 'node_'+tnm_name+'_'+node_type; /* node_T_tnm  */
    this.div_id = 'nodediv_'+tnm_name+'_'+node_type; /* nodediv_T_memo */
    this.node_type = node_type; /* tnm, memo */
    this.tnm_name = tnm_name;
    this.node_width = $("#frame").width() - 24;
    this.node_title = (node_type=='memo')?"说明":"";
    this.page_id = page_id;

    this.content_html = function(){
        var div_html = "";
        var node_text = "";

        if (this.node_type=='memo'){
            node_text = this.node_data;
            //div_html += text2HTML(node_text);
            div_html += node_text;
        }
        else if (this.node_type=='tnm'){
            var tnm_name = this.tnm_name;
            $.each(this.node_data, function(index, value){
                var t = value['code'];
                var code = t[0]+t[1]+t[2]+t[3]+t[4];
                code += (t[5].length==0)?'':'('+t[5]+')'; 
                var is_grey = (value.hasOwnProperty('grey'))?value['grey']==1:false;
                if (!is_grey)
                    node_text = '{' + code + '} : ' + value['desc'] + '\n';
                else
                    node_text = code + ' : ' + value['desc'] + '\n';
                div_html += text2HTML0(node_text, code, tnm_name, true, is_grey);
            });
        }
        div_html +="<div><a style=\"float:right;color:#537380;font-size:10px;\" href=\"#\" onclick=\"correct_click('"+this.page_id+"');\">我要纠错</a></div>";
        return div_html;
    };

    this.title_html = function(){
        if (this.node_title.length>0)
            return '<div class="desc">' + text2HTML(this.node_title) + '</div>';
        else
            return '';
    };

    this.node_html = function(){
        return '<div id="'+this.node_id+'" class="draggable" style="width: '+ this.node_width +'px;">'
            + this.title_html()
            + '<div>' + this.content_html() + '</div></div>';
    };

    this.appendToPaper = function(){
        var div = $("#"+this.node_id);
        if (div.length==0){
            $("#"+this.div_id).append(this.node_html()); /*  生成节点 */           
        }
    };

    this.border_color = function(color_num){
        $("#"+this.node_id).css("border-color",color_num);
    };
}


/* 我要纠错 click */
function correct_click(node_id){
    var session_id = $("#session_id").val();

    console.log(node_id);
    
    var dlgContentHTML = '<div id="dlgContentHTML"><p> 请填写反馈内容 </p>'+ 
        '<textarea class="ajs-input" style="width: -webkit-fill-available;" rows="6" id="correct_note"></textarea>'+ 
        '</div>';
    
    //console.log(dlgContentHTML);

    if ($("#dlgContentHTML").length>0){
        $('#correct_note').val("");
    }

    /* Now instead of making a prompt Dialog , use a Confirm Dialog */
    alertify.confirm2(dlgContentHTML).set('onok', function(closeevent, value) { 
        var correct_note = $('#correct_note').val().trim();
        //console.log(correct_note); 

        if (correct_note.length>0)
            wx_interface(
                "correct",
                {
                    session_id   : session_id,
                    node_id      : node_id,
                    correct_note : correct_note,
                    source       : "tnm",
                },
                function(data){
                    alertify.success("已提交。感谢您的支持与帮助！");
                    TDAPP.onEvent("反馈留言", "提交成功"); 
                }
            );
        else
            alertify.success("未填写反馈内容。");

    }).set('title',"我要纠错");

    TDAPP.onEvent("反馈留言", "打开窗口"); 

    return false;
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


